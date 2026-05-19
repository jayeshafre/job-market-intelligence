"""
api/routers/ai.py
=================
HTTP endpoints for the AI Assistant — Phase 2 update.

Endpoints:
  POST /api/v1/ai/chat      → Phase 1 (generic, kept for compatibility)
  POST /api/v1/ai/chat/v2   → Phase 2 (orchestrated, intent-aware)
  GET  /api/v1/ai/health    → Config check (unchanged)
  GET  /api/v1/ai/intents   → NEW: lists all supported intents

Place this file at: backend/api/routers/ai.py
"""

import logging

from fastapi import APIRouter, HTTPException

from api.config import get_settings
from api.schemas.ai import ChatRequest, ChatResponse, OrchestratedChatResponse
from api.services.ai import ask_groq, orchestrated_ask
from api.core.orchestrator import Intent
from sqlalchemy.orm import Session
from api.database import get_db
from api.schemas.ai import KPIEnrichedChatResponse
from api.services.ai import kpi_enriched_ask
from fastapi import Depends

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# POST /api/v1/ai/chat  (Phase 1 — kept unchanged)
# =============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the AI Assistant (Phase 1 — generic)",
    description=(
        "Generic AI chat endpoint. Uses a single system prompt for all questions. "
        "Kept for backward compatibility. Use /chat/v2 for better answers."
    ),
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = ask_groq(question=request.question, context=request.context)
        return ChatResponse(**result)
    except RuntimeError as e:
        logger.error(f"[AI router] /chat error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# POST /api/v1/ai/chat/v2  (Phase 2 — orchestrated)
# =============================================================================

@router.post(
    "/chat/v2",
    response_model=OrchestratedChatResponse,
    summary="Ask the AI Assistant (Phase 2 — intent-aware)",
    description=(
        "Orchestrated AI chat endpoint. Detects the question intent "
        "(salary / skills / hiring / ai_disruption / forecast / general) "
        "and uses a specialized system prompt for each intent. "
        "Produces more focused, expert-level answers than /chat."
    ),
)
def chat_v2(request: ChatRequest) -> OrchestratedChatResponse:
    """
    Phase 2 orchestrated endpoint.

    Example request:
        POST /api/v1/ai/chat/v2
        {
            "question": "Which jobs are safest from AI automation?",
            "context": "workforce intelligence"
        }

    Example response:
        {
            "answer": "Jobs with the lowest automation risk include...",
            "model": "llama-3.1-8b-instant",
            "tokens_used": 342,
            "question": "Which jobs are safest from AI automation?",
            "detected_intent": "ai_disruption"
        }
    """
    try:
        result = orchestrated_ask(question=request.question, context=request.context)
        return OrchestratedChatResponse(**result)
    except RuntimeError as e:
        logger.error(f"[AI router] /chat/v2 error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat/v2 unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# GET /api/v1/ai/intents  (NEW in Phase 2)
# =============================================================================

@router.get(
    "/intents",
    summary="List all supported question intents",
    description=(
        "Returns all intent categories the orchestrator can detect. "
        "Useful for the frontend to show intent labels and icons."
    ),
)
def list_intents() -> dict:
    """
    Returns all supported intents with descriptions.
    No Groq call — pure metadata endpoint.
    """
    return {
        "intents": [
            {
                "intent": Intent.SALARY.value,
                "description": "Questions about salaries, pay, compensation, earnings",
                "example": "What is the average salary for a Data Scientist in the US?",
            },
            {
                "intent": Intent.SKILLS.value,
                "description": "Questions about skills, technologies, learning, demand",
                "example": "Which skills are growing fastest in 2024?",
            },
            {
                "intent": Intent.HIRING.value,
                "description": "Questions about hiring trends, job postings, recruitment",
                "example": "Which industries are hiring the most right now?",
            },
            {
                "intent": Intent.AI_DISRUPTION.value,
                "description": "Questions about automation risk, AI disruption, job safety",
                "example": "Which jobs are safest from AI automation?",
            },
            {
                "intent": Intent.FORECAST.value,
                "description": "Questions about future trends, predictions, forecasts",
                "example": "What will the demand for ML engineers look like in 2026?",
            },
            {
                "intent": Intent.GENERAL.value,
                "description": "General workforce analytics questions (fallback)",
                "example": "Tell me about the global job market in 2024.",
            },
        ]
    }

# =============================================================================
# POST /api/v1/ai/chat/v3  (Phase 3 — KPI-enriched, data-backed answers)
# =============================================================================
 
@router.post(
    "/chat/v3",
    response_model=KPIEnrichedChatResponse,
    summary="Ask the AI Assistant (Phase 3 — KPI data-backed)",
    description=(
        "The most powerful AI endpoint. Detects intent, queries real platform "
        "KPIs from the database, injects them into the prompt, then calls Groq. "
        "Answers are grounded in your actual warehouse data (salaries, skills, "
        "hiring trends, AI disruption scores). "
        "Returns kpi_context_used=true when real data was injected."
    ),
)
def chat_v3(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> KPIEnrichedChatResponse:
    """
    Phase 3 KPI-enriched endpoint.
 
    This endpoint does more work than v1/v2:
      1. Detects intent
      2. Queries your PostgreSQL warehouse for real KPIs
      3. Injects KPIs into the system prompt
      4. Calls Groq with enriched context
 
    The db: Session = Depends(get_db) injects a database session.
    This is the same pattern used in all your analytics routers.
 
    Example request:
        POST /api/v1/ai/chat/v3
        {
            "question": "Which skills are growing fastest in 2024?",
            "context": "workforce intelligence"
        }
 
    Example response:
        {
            "answer": "Based on your platform data, the fastest growing skills
                       in 2024 are: LLM Engineering [AI/ML] with 35.2% growth...",
            "model": "llama-3.1-8b-instant",
            "tokens_used": 487,
            "question": "Which skills are growing fastest in 2024?",
            "detected_intent": "skills",
            "kpi_context_used": true
        }
    """
    try:
        result = kpi_enriched_ask(
            question=request.question,
            context=request.context,
            db=db,
        )
        return KPIEnrichedChatResponse(**result)
 
    except RuntimeError as e:
        logger.error(f"[AI router] /chat/v3 error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
 
    except Exception as e:
        logger.exception(f"[AI router] /chat/v3 unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")

# =============================================================================
# GET /api/v1/ai/health  (unchanged from Phase 1)
# =============================================================================

@router.get(
    "/health",
    summary="Check AI service configuration",
    description="Verifies Groq API key is configured. Does NOT make a real API call.",
)
def ai_health() -> dict:
    settings = get_settings()
    configured = bool(settings.GROQ_API_KEY)
    return {
        "ai_service": "groq",
        "configured": configured,
        "model": settings.GROQ_MODEL,
        "status": "ready" if configured else "missing_api_key",
    }