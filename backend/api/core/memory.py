"""
api/core/memory.py
==================
Conversational Memory with Redis — Phase 7.

Stores and retrieves conversation history per session so the AI
remembers what was said in previous turns of the same conversation.

Why Redis for memory?
  Redis is an in-memory key-value store — the fastest possible storage
  for session data. Every production AI assistant uses something like
  this under the hood:
    ChatGPT     → Azure Cosmos DB / Redis
    Claude      → Internal session store
    LangChain   → RedisMemory / ConversationBufferMemory

  Key properties we use:
    SET with EX  → automatic TTL expiry (conversations auto-delete)
    JSON storage → full message history in one key
    APPEND       → O(1) message addition per turn

Data structure in Redis:
  Key:   "session:{session_id}"
  Value: JSON array of message dicts
  TTL:   3600 seconds (1 hour) — reset on every new message

  Example value:
    [
      {"role": "user",      "content": "Which jobs are safest from AI?"},
      {"role": "assistant", "content": "The safest careers include..."},
      {"role": "user",      "content": "Why are ML engineers safe?"},
      {"role": "assistant", "content": "ML Engineers are safe because..."}
    ]

  This array is injected between the system prompt and the new user
  message, giving the LLM full conversation context.

Place this file at: backend/api/core/memory.py
"""

import json
import logging
import uuid
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# Max number of turns to keep in memory.
# Each turn = 1 user message + 1 assistant message = 2 entries.
# 10 turns = 20 messages max in context window.
# Beyond this we trim oldest turns — prevents context overflow.
MAX_TURNS = 10


# =============================================================================
# REDIS CLIENT (singleton)
# =============================================================================

@lru_cache(maxsize=1)
def get_redis_client():
    """
    Creates and caches a single Redis client for the application lifetime.

    Why lru_cache?
      Same pattern as get_groq_client() and get_embedding_model().
      One connection pool, reused across all requests.

    Returns:
        redis.Redis client instance.

    Raises:
        RuntimeError if redis package not installed or connection fails.
    """
    try:
        import redis
        from api.config import get_settings
        settings = get_settings()

        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,   # return strings, not bytes
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        # Test connection immediately — fail fast at startup
        client.ping()
        logger.info(f"[MEMORY] Redis connected at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return client

    except ImportError:
        raise RuntimeError("redis not installed. Run: pip install redis==5.0.1")
    except Exception as e:
        raise RuntimeError(f"Redis connection failed: {e}. Is Redis running?")


def is_redis_available() -> bool:
    """
    Checks if Redis is reachable without raising an exception.
    Used for graceful degradation — if Redis is down, fall back to stateless mode.
    """
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception:
        return False


# =============================================================================
# SESSION KEY HELPERS
# =============================================================================

def make_session_key(session_id: str) -> str:
    """Namespaced Redis key for a conversation session."""
    return f"session:{session_id}"


def generate_session_id() -> str:
    """
    Generates a new unique session ID.
    UUIDs are the industry standard for session identifiers —
    statistically impossible to collide, no sequential guessing.
    """
    return str(uuid.uuid4())


# =============================================================================
# MEMORY OPERATIONS
# =============================================================================

def get_history(session_id: str) -> list[dict]:
    """
    Retrieves the conversation history for a session from Redis.

    Args:
        session_id: The unique session identifier.

    Returns:
        List of message dicts [{"role": ..., "content": ...}, ...]
        Returns empty list if session doesn't exist or Redis is down.
    """
    try:
        client = get_redis_client()
        key    = make_session_key(session_id)
        raw    = client.get(key)

        if not raw:
            logger.info(f"[MEMORY] No history for session={session_id} (new session)")
            return []

        history = json.loads(raw)
        logger.info(f"[MEMORY] Loaded {len(history)} messages for session={session_id}")
        return history

    except Exception as e:
        logger.warning(f"[MEMORY] get_history failed for session={session_id}: {e}")
        return []   # graceful degradation — AI still works, just without memory


def save_turn(
    session_id: str,
    user_message: str,
    assistant_message: str,
    ttl_seconds: Optional[int] = None,
) -> bool:
    """
    Appends a user+assistant turn to the conversation history and saves to Redis.

    Args:
        session_id:        The session to update.
        user_message:      The user's question for this turn.
        assistant_message: The AI's response for this turn.
        ttl_seconds:       TTL for the key. Defaults to config value.

    Returns:
        True if saved successfully, False on error.
    """
    try:
        from api.config import get_settings
        client     = get_redis_client()
        key        = make_session_key(session_id)
        ttl        = ttl_seconds or get_settings().REDIS_TTL_SECONDS

        # Load existing history
        history = get_history(session_id)

        # Append the new turn
        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant", "content": assistant_message})

        # Trim to MAX_TURNS (keep most recent turns)
        # Each turn = 2 messages, so max messages = MAX_TURNS * 2
        max_messages = MAX_TURNS * 2
        if len(history) > max_messages:
            trimmed = len(history) - max_messages
            history = history[trimmed:]
            logger.info(f"[MEMORY] Trimmed {trimmed} old messages for session={session_id}")

        # Save back to Redis with refreshed TTL
        client.setex(key, ttl, json.dumps(history))

        logger.info(
            f"[MEMORY] Saved turn for session={session_id} | "
            f"total_messages={len(history)} | ttl={ttl}s"
        )
        return True

    except Exception as e:
        logger.warning(f"[MEMORY] save_turn failed for session={session_id}: {e}")
        return False


def clear_session(session_id: str) -> bool:
    """
    Deletes a conversation session from Redis.
    Called when the user wants to start a fresh conversation.

    Returns:
        True if deleted, False if key didn't exist or error.
    """
    try:
        client  = get_redis_client()
        key     = make_session_key(session_id)
        deleted = client.delete(key)
        logger.info(f"[MEMORY] Cleared session={session_id} (deleted={deleted})")
        return deleted > 0
    except Exception as e:
        logger.warning(f"[MEMORY] clear_session failed: {e}")
        return False


def get_session_info(session_id: str) -> dict:
    """
    Returns metadata about a session without returning full message content.
    Used by the /memory/status endpoint.
    """
    try:
        client  = get_redis_client()
        key     = make_session_key(session_id)
        raw     = client.get(key)
        ttl     = client.ttl(key)

        if not raw:
            return {"session_id": session_id, "exists": False, "turn_count": 0, "ttl_seconds": 0}

        history    = json.loads(raw)
        turn_count = len(history) // 2   # 2 messages per turn

        return {
            "session_id":  session_id,
            "exists":      True,
            "turn_count":  turn_count,
            "message_count": len(history),
            "ttl_seconds": ttl,
        }
    except Exception as e:
        logger.warning(f"[MEMORY] get_session_info failed: {e}")
        return {"session_id": session_id, "exists": False, "error": str(e)}


# =============================================================================
# PROMPT BUILDER WITH HISTORY
# =============================================================================

def build_messages_with_history(
    system_prompt: str,
    history: list[dict],
    current_question: str,
    user_message_content: str,
) -> list[dict]:
    """
    Assembles the full messages array for the Groq API call,
    including conversation history between the system prompt and the new message.

    Why inject history between system and user?
      The Groq/OpenAI messages format is:
        [system, user, assistant, user, assistant, ..., user]
      The system prompt always goes first.
      History turns go in the middle.
      The new user message goes last.

    Args:
        system_prompt:        The enriched system prompt (persona + KPI + RAG).
        history:              Previous turns from Redis.
        current_question:     The raw user question (for logging).
        user_message_content: The formatted user message with context.

    Returns:
        List of message dicts ready for client.chat.completions.create().
    """
    messages = [{"role": "system", "content": system_prompt}]

    # Inject history turns (already formatted as role/content dicts)
    messages.extend(history)

    # Add the current user message
    messages.append({"role": "user", "content": user_message_content})

    logger.info(
        f"[MEMORY] Built messages array: system(1) + history({len(history)}) "
        f"+ current(1) = {len(messages)} total messages"
    )
    return messages