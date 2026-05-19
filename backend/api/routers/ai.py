"""
api/routers/ai.py
=================
HTTP endpoints for the AI Assistant — Phase 1.

This router is intentionally thin. Its only job is:
  1. Accept the HTTP request
  2. Validate the request body (Pydantic does this automatically)
  3. Call the service layer
  4. Return a structured JSON response

All AI logic lives in api/services/ai.py — not here.

Place this file at: backend/api/routers/ai.py
"""

import logging

from fastapi import APIRouter, HTTPException

from api.schemas.ai import ChatRequest, ChatResponse
from api.services.ai import ask_groq
from api.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# POST /api/v1/ai/chat
# =============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the AI Workforce Analytics Assistant",
    description=(
        "Send a natural language question about the global job market. "
        "The AI assistant answers using its knowledge of hiring trends, "
        "salaries, skills, and AI disruption."
    ),
)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Main AI chat endpoint.

    Example request:
        POST /api/v1/ai/chat
        {
            "question": "Which jobs are safest from AI automation?",
            "context": "workforce intelligence"
        }

    Example response:
        {
            "answer": "Jobs safest from AI automation tend to be...",
            "model": "llama-3.1-8b-instant",
            "tokens_used": 287,
            "question": "Which jobs are safest from AI automation?"
        }
    """
    try:
        result = ask_groq(
            question=request.question,
            context=request.context,
        )
        return ChatResponse(**result)

    except RuntimeError as e:
        # RuntimeError from our service = a clean, user-facing error message
        logger.error(f"[AI router] Service error: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        # Catch-all for anything unexpected
        logger.exception(f"[AI router] Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred in the AI service.",
        )


# =============================================================================
# GET /api/v1/ai/health
# =============================================================================

@router.get(
    "/health",
    summary="Check AI service configuration",
    description="Verifies that the Groq API key is configured. Does NOT make a real API call.",
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