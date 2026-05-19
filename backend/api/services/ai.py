"""
api/services/ai.py
==================
AI service layer — Phase 2 update.

Phase 1: ask_groq()         — single generic function, one system prompt
Phase 2: orchestrated_ask() — routes through the orchestrator, intent-specific prompts

Both functions are kept. ask_groq() still powers /chat (Phase 1 endpoint).
orchestrated_ask() powers /chat/v2 (Phase 2 endpoint).

This is backward-compatible — nothing breaks when you add Phase 2.

Place this file at: backend/api/services/ai.py
"""

import logging

from groq import APIConnectionError, APIStatusError, RateLimitError

from api.core.groq_client import get_groq_client, get_groq_model
from api.core.orchestrator import orchestrate

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 1 — SYSTEM PROMPT (kept as-is)
# =============================================================================

SYSTEM_PROMPT = """You are an expert AI Workforce Analytics Assistant for a 
global job market intelligence platform.

Your role is to answer questions about:
- Hiring trends across industries and countries
- Salary benchmarks and growth patterns by role and region
- High-demand and fastest-growing technical skills
- AI disruption risk and automation scores for job roles
- Future-safe careers and workforce transformation
- Job market forecasts and predictions

Guidelines:
- Be concise and data-driven in your answers
- When specific data is not available, provide general expert insights
- Always frame answers in the context of workforce and hiring analytics
- Use professional language suitable for HR professionals, analysts, and researchers
- If asked something outside job market / workforce topics, politely redirect
- Structure longer answers with clear sections when helpful

You have access to a platform with data on:
- Global job postings from 2018–2024
- Salary trends across 30+ countries and 80+ job roles
- Skill demand tracking for 100+ technical and soft skills
- AI disruption scores for roles across 15+ industries
"""


# =============================================================================
# PHASE 1 FUNCTION — ask_groq() (unchanged, kept for /chat endpoint)
# =============================================================================

def ask_groq(question: str, context: str) -> dict:
    """
    Phase 1 function — single generic prompt, no intent detection.
    Still powers POST /api/v1/ai/chat for backward compatibility.
    """
    client = get_groq_client()
    model = get_groq_model()

    user_message = f"Context: {context}\n\nQuestion: {question}"

    logger.info(f"[AI] ask_groq() | model={model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        return {
            "answer": response.choices[0].message.content,
            "model": model,
            "tokens_used": response.usage.total_tokens,
            "question": question,
        }

    except RateLimitError:
        logger.warning("[AI] Rate limit hit.")
        raise RuntimeError("AI service is temporarily rate-limited. Please wait and try again.")

    except APIConnectionError:
        logger.error("[AI] Connection error.")
        raise RuntimeError("Could not reach the AI service. Check your internet connection.")

    except APIStatusError as e:
        logger.error(f"[AI] API error: {e.status_code} - {e.message}")
        raise RuntimeError(f"AI service returned an error (status {e.status_code}).")


# =============================================================================
# PHASE 2 FUNCTION — orchestrated_ask() (new)
# =============================================================================

def orchestrated_ask(question: str, context: str) -> dict:
    """
    Phase 2 function — routes through the orchestrator before calling Groq.

    What's different from ask_groq():
      1. Calls orchestrate() to detect intent and select the right system prompt
      2. Uses the intent-specific system prompt instead of the generic one
      3. Returns detected_intent in the response dict

    The Groq call itself is identical — only the system prompt changes.
    That's the power of the orchestrator pattern: one LLM, many personalities.

    Args:
        question: The user's natural language question.
        context:  Optional domain context from the request.

    Returns:
        dict with keys: answer, model, tokens_used, question, detected_intent
    """
    client = get_groq_client()
    model = get_groq_model()

    # Step 1: Run the orchestrator
    # This detects intent and selects the right system prompt — zero latency.
    result = orchestrate(question=question, context=context)

    logger.info(
        f"[AI] orchestrated_ask() | intent={result.detected_intent.value} | model={model}"
    )

    try:
        # Step 2: Call Groq with the intent-specific system prompt
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": result.system_prompt},
                {"role": "user",   "content": result.user_message},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        logger.info(
            f"[AI] Response received | intent={result.detected_intent.value} | tokens={tokens_used}"
        )

        # Step 3: Return result including the detected intent
        return {
            "answer": answer,
            "model": model,
            "tokens_used": tokens_used,
            "question": question,
            "detected_intent": result.detected_intent.value,
        }

    except RateLimitError:
        logger.warning("[AI] Rate limit hit.")
        raise RuntimeError("AI service is temporarily rate-limited. Please wait and try again.")

    except APIConnectionError:
        logger.error("[AI] Connection error.")
        raise RuntimeError("Could not reach the AI service. Check your internet connection.")

    except APIStatusError as e:
        logger.error(f"[AI] API error: {e.status_code} - {e.message}")
        raise RuntimeError(f"AI service returned an error (status {e.status_code}).")