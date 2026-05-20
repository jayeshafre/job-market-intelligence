"""
api/routers/ai.py
=================
HTTP endpoints for the AI Assistant — Phase 5 complete.

Endpoints:
  POST /api/v1/ai/chat         → Phase 1: generic
  POST /api/v1/ai/chat/v2      → Phase 2: intent-aware
  POST /api/v1/ai/chat/v3      → Phase 3: KPI data-backed
  POST /api/v1/ai/chat/v4      → Phase 4: + structured recommendations
  GET  /api/v1/ai/executive-summary → Phase 5: full platform briefing
  GET  /api/v1/ai/smart-alerts      → Phase 5: threshold-based alerts
  GET  /api/v1/ai/intents      → metadata: all supported intents
  GET  /api/v1/ai/health       → config check

Place this file at: backend/api/routers/ai.py
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.config import get_settings
from api.core.orchestrator import Intent
from api.core.executive_summary import generate_executive_summary
from api.core.smart_alerts import run_smart_alerts
from api.database import get_db
from api.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ExecutiveSummaryResponse,
    KeyMetrics,
    KPIEnrichedChatResponse,
    OrchestratedChatResponse,
    RecommendationResponse,
    SmartAlert,
    SmartAlertsResponse,
)
from api.services.ai import ask_groq, kpi_enriched_ask, orchestrated_ask, recommendation_ask

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# POST /api/v1/ai/chat  (Phase 1)
# =============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the AI Assistant (Phase 1 — generic)",
    description="Generic AI chat. Single system prompt. Kept for backward compatibility.",
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = ask_groq(question=request.question, context=request.context)
        return ChatResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# POST /api/v1/ai/chat/v2  (Phase 2)
# =============================================================================

@router.post(
    "/chat/v2",
    response_model=OrchestratedChatResponse,
    summary="Ask the AI Assistant (Phase 2 — intent-aware)",
    description=(
        "Detects question intent (salary / skills / hiring / ai_disruption / "
        "forecast / general) and uses a specialized expert system prompt per intent."
    ),
)
def chat_v2(request: ChatRequest) -> OrchestratedChatResponse:
    try:
        result = orchestrated_ask(question=request.question, context=request.context)
        return OrchestratedChatResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat/v2 error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# POST /api/v1/ai/chat/v3  (Phase 3)
# =============================================================================

@router.post(
    "/chat/v3",
    response_model=KPIEnrichedChatResponse,
    summary="Ask the AI Assistant (Phase 3 — KPI data-backed)",
    description=(
        "Intent detection + real warehouse KPIs injected into the prompt. "
        "Answers grounded in your actual PostgreSQL data. "
        "Returns kpi_context_used=true when real data was injected."
    ),
)
def chat_v3(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> KPIEnrichedChatResponse:
    try:
        result = kpi_enriched_ask(
            question=request.question,
            context=request.context,
            db=db,
        )
        return KPIEnrichedChatResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat/v3 error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# POST /api/v1/ai/chat/v4  (Phase 4)
# =============================================================================

@router.post(
    "/chat/v4",
    response_model=RecommendationResponse,
    summary="Ask the AI Assistant (Phase 4 — with recommendations)",
    description=(
        "Intent + KPI data + 3 structured actionable recommendations as typed objects. "
        "Returns recommendations_parsed=true when JSON extraction succeeded."
    ),
)
def chat_v4(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    try:
        result = recommendation_ask(
            question=request.question,
            context=request.context,
            db=db,
        )
        return RecommendationResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /chat/v4 error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in AI service.")


# =============================================================================
# GET /api/v1/ai/executive-summary  (Phase 5)
# =============================================================================

@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryResponse,
    summary="Generate executive intelligence briefing (Phase 5)",
    description=(
        "Queries all 4 KPI domains (hiring, salary, skills, AI disruption), "
        "assembles a full platform snapshot, and asks Groq to write a "
        "boardroom-ready executive briefing. "
        "Returns the summary prose + structured key_metrics for the UI header strip. "
        "No question needed — call it and get a full platform intelligence report."
    ),
)
def executive_summary(
    db: Session = Depends(get_db),
) -> ExecutiveSummaryResponse:
    """
    Executive summary endpoint — no request body needed.

    Example response:
        {
            "summary": "The global job market in 2024 is defined by an accelerating
                        bifurcation between AI-augmented roles and automation-exposed
                        ones. With 149% YoY growth in Prompt Engineering demand...",
            "key_metrics": {
                "total_postings": 1250000,
                "global_avg_salary": 78432.50,
                "remote_pct": 47.3,
                "fastest_skill": "Prompt Engineering",
                "fastest_skill_growth": 149.03,
                "highest_risk_role": "Data Entry Clerk",
                "safest_career": "Clinical Psychologist"
            },
            "generated_at": "2024-01-15T09:30:00Z",
            "tokens_used": 521,
            "model": "llama-3.1-8b-instant"
        }
    """
    try:
        result = generate_executive_summary(db)
        return ExecutiveSummaryResponse(
            summary=result["summary"],
            key_metrics=KeyMetrics(**result["key_metrics"]),
            generated_at=result["generated_at"],
            tokens_used=result["tokens_used"],
            model=result["model"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[AI router] /executive-summary error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error generating summary.")


# =============================================================================
# GET /api/v1/ai/smart-alerts  (Phase 5)
# =============================================================================

@router.get(
    "/smart-alerts",
    response_model=SmartAlertsResponse,
    summary="Run smart alert scan (Phase 5)",
    description=(
        "Scans all KPI data against predefined thresholds and returns typed alerts. "
        "No LLM call — pure deterministic data analysis. Always fast, always fresh. "
        "Alerts are sorted: critical → warning → info. "
        "Severity: critical (>80 risk / >100% growth), "
        "warning (>65 risk / >50% growth), info (notable trends)."
    ),
)
def smart_alerts(
    db: Session = Depends(get_db),
) -> SmartAlertsResponse:
    """
    Smart alerts endpoint — no request body needed.

    Example response:
        {
            "alerts": [
                {
                    "severity": "critical",
                    "category": "skill_surge",
                    "title": "Explosive skill surge: Prompt Engineering",
                    "message": "Prompt Engineering has grown 149.0% YoY...",
                    "data_point": 149.03,
                    "entity": "Prompt Engineering"
                },
                ...
            ],
            "alert_count": 12,
            "critical_count": 3,
            "warning_count": 7,
            "info_count": 2,
            "scanned_at": "2024-01-15T09:30:00Z"
        }
    """
    try:
        result = run_smart_alerts(db)
        alerts = [SmartAlert(**a) for a in result["alerts"]]
        return SmartAlertsResponse(
            alerts=alerts,
            alert_count=result["alert_count"],
            critical_count=result["critical_count"],
            warning_count=result["warning_count"],
            info_count=result["info_count"],
            scanned_at=result["scanned_at"],
        )
    except Exception as e:
        logger.exception(f"[AI router] /smart-alerts error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error running alert scan.")


# =============================================================================
# GET /api/v1/ai/intents  (Phase 2 — unchanged)
# =============================================================================

@router.get(
    "/intents",
    summary="List all supported question intents",
    description="Returns all intent categories the orchestrator can detect.",
)
def list_intents() -> dict:
    return {
        "intents": [
            {"intent": Intent.SALARY.value,        "description": "Questions about salaries, pay, compensation",         "example": "What is the average salary for a Data Scientist?"},
            {"intent": Intent.SKILLS.value,         "description": "Questions about skills, technologies, demand",         "example": "Which skills are growing fastest in 2024?"},
            {"intent": Intent.HIRING.value,         "description": "Questions about hiring trends, job postings",          "example": "Which industries are hiring the most right now?"},
            {"intent": Intent.AI_DISRUPTION.value,  "description": "Questions about automation risk, AI disruption",       "example": "Which jobs are safest from AI automation?"},
            {"intent": Intent.FORECAST.value,       "description": "Questions about future trends, predictions",           "example": "What will ML engineer demand look like in 2026?"},
            {"intent": Intent.GENERAL.value,        "description": "General workforce analytics questions (fallback)",     "example": "Tell me about the global job market in 2024."},
        ]
    }


# =============================================================================
# GET /api/v1/ai/health  (Phase 1 — unchanged)
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
        "model":      settings.GROQ_MODEL,
        "status":     "ready" if configured else "missing_api_key",
    }