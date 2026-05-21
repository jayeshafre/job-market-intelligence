"""
api/routers/ai.py
=================
HTTP endpoints for the AI Assistant — Phase 7 complete.

Endpoints:
  POST /api/v1/ai/chat              → Phase 1: generic
  POST /api/v1/ai/chat/v2           → Phase 2: intent-aware
  POST /api/v1/ai/chat/v3           → Phase 3: KPI data-backed
  POST /api/v1/ai/chat/v4           → Phase 4: + recommendations
  POST /api/v1/ai/chat/v5           → Phase 6: + RAG retrieval
  POST /api/v1/ai/chat/v6           → Phase 7: + Redis conversation memory
  GET  /api/v1/ai/executive-summary → Phase 5: executive briefing
  GET  /api/v1/ai/smart-alerts      → Phase 5: threshold alerts
  POST /api/v1/ai/rag/index         → Phase 6: index documents
  GET  /api/v1/ai/rag/status        → Phase 6: vector store status
  DELETE /api/v1/ai/memory/{id}     → Phase 7: clear session memory
  GET    /api/v1/ai/memory/{id}     → Phase 7: session info
  GET  /api/v1/ai/intents           → metadata
  GET  /api/v1/ai/health            → config check

Place this file at: backend/api/routers/ai.py
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.config import get_settings
from api.core.orchestrator import Intent
from api.core.executive_summary import generate_executive_summary
from api.core.smart_alerts import run_smart_alerts
from api.core.rag_pipeline import (
    index_documents, retrieve_relevant_chunks,
    format_rag_context, get_or_create_collection,
)
from api.core.memory import (
    get_history, save_turn, clear_session,
    get_session_info, generate_session_id,
    build_messages_with_history, is_redis_available,
)
from api.database import get_db
from api.schemas.ai import (
    ChatRequest, ChatResponse,
    ExecutiveSummaryResponse, KeyMetrics,
    KPIEnrichedChatResponse, OrchestratedChatResponse,
    RAGChatResponse, RecommendationResponse,
    RetrievedChunk, SmartAlert, SmartAlertsResponse,
    MemoryChatRequest, MemoryChatResponse,
)
from api.services.ai import ask_groq, kpi_enriched_ask, orchestrated_ask, recommendation_ask

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# POST /chat  (Phase 1)
# =============================================================================

@router.post("/chat", response_model=ChatResponse,
             summary="Phase 1 — generic")
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return ChatResponse(**ask_groq(question=request.question, context=request.context))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /chat: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /chat/v2  (Phase 2)
# =============================================================================

@router.post("/chat/v2", response_model=OrchestratedChatResponse,
             summary="Phase 2 — intent-aware")
def chat_v2(request: ChatRequest) -> OrchestratedChatResponse:
    try:
        return OrchestratedChatResponse(
            **orchestrated_ask(question=request.question, context=request.context)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /chat/v2: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /chat/v3  (Phase 3)
# =============================================================================

@router.post("/chat/v3", response_model=KPIEnrichedChatResponse,
             summary="Phase 3 — KPI data-backed")
def chat_v3(request: ChatRequest, db: Session = Depends(get_db)) -> KPIEnrichedChatResponse:
    try:
        return KPIEnrichedChatResponse(
            **kpi_enriched_ask(question=request.question, context=request.context, db=db)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /chat/v3: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /chat/v4  (Phase 4)
# =============================================================================

@router.post("/chat/v4", response_model=RecommendationResponse,
             summary="Phase 4 — with recommendations")
def chat_v4(request: ChatRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    try:
        return RecommendationResponse(
            **recommendation_ask(question=request.question, context=request.context, db=db)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /chat/v4: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /chat/v5  (Phase 6 — RAG)
# =============================================================================

@router.post("/chat/v5", response_model=RAGChatResponse,
             summary="Phase 6 — RAG + KPI + Recommendations")
def chat_v5(request: ChatRequest, db: Session = Depends(get_db)) -> RAGChatResponse:
    from api.core.kpi_context import build_kpi_context
    from api.core.orchestrator import orchestrate
    from api.core.recommendation_engine import build_recommendation_prompt, parse_recommendations
    from api.core.groq_client import get_groq_client, get_groq_model
    from groq import APIConnectionError, APIStatusError, RateLimitError

    client = get_groq_client()
    model  = get_groq_model()

    try:
        orch_result      = orchestrate(question=request.question, context=request.context)
        kpi_block        = build_kpi_context(intent=orch_result.detected_intent, db=db)
        kpi_context_used = bool(kpi_block)
        raw_chunks       = retrieve_relevant_chunks(query=request.question, top_k=3)
        rag_block        = format_rag_context(raw_chunks)
        rag_used         = bool(rag_block)
        rec_prompt       = build_recommendation_prompt(intent=orch_result.detected_intent, kpi_context=kpi_block)

        parts = [orch_result.system_prompt]
        if kpi_block:  parts.append(kpi_block)
        if rag_block:  parts.append(rag_block)
        parts.append(rec_prompt)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "\n\n".join(parts)},
                {"role": "user",   "content": orch_result.user_message},
            ],
            temperature=0.3, max_tokens=1400,
        )

        raw_answer  = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        parsed      = parse_recommendations(raw_answer)

        return RAGChatResponse(
            answer=parsed.clean_answer, model=model, tokens_used=tokens_used,
            question=request.question, detected_intent=orch_result.detected_intent.value,
            kpi_context_used=kpi_context_used, rag_used=rag_used,
            chunks_retrieved=len(raw_chunks),
            retrieved_chunks=[RetrievedChunk(**c) for c in raw_chunks],
            recommendations=parsed.recommendations, recommendations_parsed=parsed.parse_success,
        )
    except (RateLimitError, APIConnectionError, APIStatusError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /chat/v5: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /chat/v6  (Phase 7 — Redis Memory)
# =============================================================================

@router.post(
    "/chat/v6",
    response_model=MemoryChatResponse,
    summary="Phase 7 — Full stack + Redis conversation memory",
    description=(
        "The complete AI pipeline with persistent conversational memory. "
        "Pass session_id=null to start a new conversation. "
        "Reuse the returned session_id in subsequent requests to maintain context. "
        "Memory auto-expires after 1 hour of inactivity. "
        "Falls back to stateless mode gracefully if Redis is unavailable."
    ),
)
def chat_v6(
    request: MemoryChatRequest,
    db: Session = Depends(get_db),
) -> MemoryChatResponse:
    """
    Phase 7 — the full intelligence stack with memory.

    Turn 1: { "question": "Which jobs are safest from AI?", "session_id": null }
    Turn 2: { "question": "Why are ML engineers specifically safe?", "session_id": "<returned_id>" }
    Turn 3: { "question": "What salary can I expect?", "session_id": "<returned_id>" }

    The AI remembers the full conversation and answers in context.
    """
    from api.core.kpi_context import build_kpi_context
    from api.core.orchestrator import orchestrate
    from api.core.recommendation_engine import build_recommendation_prompt, parse_recommendations
    from api.core.groq_client import get_groq_client, get_groq_model
    from groq import APIConnectionError, APIStatusError, RateLimitError

    client = get_groq_client()
    model  = get_groq_model()

    # ── Session Management ─────────────────────────────────────────────────
    # If no session_id provided, start a fresh conversation
    session_id     = request.session_id or generate_session_id()
    is_new_session = request.session_id is None
    redis_ok       = is_redis_available()

    # ── Load Conversation History ──────────────────────────────────────────
    history     = get_history(session_id) if redis_ok else []
    memory_used = bool(history)
    turn_count  = len(history) // 2   # 2 messages per turn

    logger.info(
        f"[AI] /chat/v6 | session={session_id} | "
        f"new={is_new_session} | turns={turn_count} | redis={redis_ok}"
    )

    try:
        # ── Build the enriched prompt (same as v5) ─────────────────────────
        orch_result      = orchestrate(question=request.question, context=request.context)
        kpi_block        = build_kpi_context(intent=orch_result.detected_intent, db=db)
        kpi_context_used = bool(kpi_block)
        raw_chunks       = retrieve_relevant_chunks(query=request.question, top_k=3)
        rag_block        = format_rag_context(raw_chunks)
        rag_used         = bool(rag_block)
        rec_prompt       = build_recommendation_prompt(
            intent=orch_result.detected_intent, kpi_context=kpi_block
        )

        parts = [orch_result.system_prompt]
        if kpi_block:  parts.append(kpi_block)
        if rag_block:  parts.append(rag_block)
        parts.append(rec_prompt)
        enriched_system_prompt = "\n\n".join(parts)

        # ── Build messages with conversation history ───────────────────────
        # This is the Phase 7 addition — history injected between system + user
        messages = build_messages_with_history(
            system_prompt        = enriched_system_prompt,
            history              = history,
            current_question     = request.question,
            user_message_content = orch_result.user_message,
        )

        # ── Call Groq with full conversation context ───────────────────────
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1400,
        )

        raw_answer  = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        parsed      = parse_recommendations(raw_answer)

        # ── Save this turn to Redis ────────────────────────────────────────
        if redis_ok:
            save_turn(
                session_id        = session_id,
                user_message      = request.question,
                assistant_message = parsed.clean_answer,
            )
            turn_count += 1   # reflect the turn we just completed

        logger.info(
            f"[AI] /chat/v6 done | session={session_id} | turns={turn_count} | "
            f"tokens={tokens_used} | memory={memory_used} | rag={rag_used}"
        )

        return MemoryChatResponse(
            answer                = parsed.clean_answer,
            model                 = model,
            tokens_used           = tokens_used,
            question              = request.question,
            detected_intent       = orch_result.detected_intent.value,
            kpi_context_used      = kpi_context_used,
            rag_used              = rag_used,
            chunks_retrieved      = len(raw_chunks),
            recommendations       = parsed.recommendations,
            recommendations_parsed= parsed.parse_success,
            session_id            = session_id,
            turn_count            = turn_count,
            memory_used           = memory_used,
            is_new_session        = is_new_session,
        )

    except RateLimitError:
        raise HTTPException(status_code=503, detail="AI rate-limited. Try again shortly.")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not reach AI service.")
    except APIStatusError as e:
        raise HTTPException(status_code=503, detail=f"AI service error ({e.status_code}).")
    except Exception as e:
        logger.exception(f"[AI] /chat/v6 unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# DELETE /memory/{session_id}  (Phase 7)
# =============================================================================

@router.delete(
    "/memory/{session_id}",
    summary="Clear conversation memory for a session",
    description="Deletes the Redis key for this session. The next message will start fresh.",
)
def clear_memory(session_id: str) -> dict:
    deleted = clear_session(session_id)
    return {
        "session_id": session_id,
        "cleared":    deleted,
        "message":    "Session cleared." if deleted else "Session not found or already expired.",
    }


# =============================================================================
# GET /memory/{session_id}  (Phase 7)
# =============================================================================

@router.get(
    "/memory/{session_id}",
    summary="Get conversation session info",
    description="Returns metadata about a session: turn count, TTL remaining, existence.",
)
def memory_status(session_id: str) -> dict:
    return get_session_info(session_id)


# =============================================================================
# GET /executive-summary  (Phase 5)
# =============================================================================

@router.get("/executive-summary", response_model=ExecutiveSummaryResponse,
            summary="Phase 5 — Executive intelligence briefing")
def executive_summary(db: Session = Depends(get_db)) -> ExecutiveSummaryResponse:
    try:
        result = generate_executive_summary(db)
        return ExecutiveSummaryResponse(
            summary=result["summary"], key_metrics=KeyMetrics(**result["key_metrics"]),
            generated_at=result["generated_at"], tokens_used=result["tokens_used"],
            model=result["model"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI] /executive-summary: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# GET /smart-alerts  (Phase 5)
# =============================================================================

@router.get("/smart-alerts", response_model=SmartAlertsResponse,
            summary="Phase 5 — Smart threshold alerts")
def smart_alerts(db: Session = Depends(get_db)) -> SmartAlertsResponse:
    try:
        result = run_smart_alerts(db)
        return SmartAlertsResponse(
            alerts=[SmartAlert(**a) for a in result["alerts"]],
            alert_count=result["alert_count"], critical_count=result["critical_count"],
            warning_count=result["warning_count"], info_count=result["info_count"],
            scanned_at=result["scanned_at"],
        )
    except Exception as e:
        logger.exception(f"[AI] /smart-alerts: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error.")


# =============================================================================
# POST /rag/index  (Phase 6)
# =============================================================================

@router.post("/rag/index", summary="Phase 6 — Index documents into ChromaDB")
def rag_index(
    force_reindex: bool = Query(default=False)
) -> dict:
    try:
        return {"success": True, **index_documents(force_reindex=force_reindex)}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[RAG] Indexing error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error during indexing.")


# =============================================================================
# GET /rag/status  (Phase 6)
# =============================================================================

@router.get("/rag/status", summary="Phase 6 — Vector store status")
def rag_status() -> dict:
    try:
        collection = get_or_create_collection()
        count      = collection.count()
        return {
            "collection":    "job_market_intelligence",
            "chunks_stored": count,
            "status":        "ready" if count > 0 else "empty — run /rag/index first",
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# =============================================================================
# GET /intents
# =============================================================================

@router.get("/intents", summary="List all supported question intents")
def list_intents() -> dict:
    return {
        "intents": [
            {"intent": Intent.SALARY.value,       "description": "Salaries, pay, compensation",          "example": "What is the avg salary for a Data Scientist?"},
            {"intent": Intent.SKILLS.value,        "description": "Skills, technologies, demand",         "example": "Which skills are growing fastest in 2024?"},
            {"intent": Intent.HIRING.value,        "description": "Hiring trends, job postings",          "example": "Which industries are hiring the most?"},
            {"intent": Intent.AI_DISRUPTION.value, "description": "Automation risk, AI disruption",       "example": "Which jobs are safest from AI automation?"},
            {"intent": Intent.FORECAST.value,      "description": "Future trends, predictions",           "example": "What will ML engineer demand look like in 2026?"},
            {"intent": Intent.GENERAL.value,       "description": "General workforce analytics questions","example": "Tell me about the global job market in 2024."},
        ]
    }


# =============================================================================
# GET /health
# =============================================================================

@router.get("/health", summary="AI service config check")
def ai_health() -> dict:
    settings   = get_settings()
    configured = bool(settings.GROQ_API_KEY)
    return {
        "ai_service":  "groq",
        "configured":  configured,
        "model":       settings.GROQ_MODEL,
        "status":      "ready" if configured else "missing_api_key",
        "redis":       "available" if is_redis_available() else "unavailable",
    }