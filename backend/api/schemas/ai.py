"""
api/schemas/ai.py
=================
Pydantic request and response models for the AI chat endpoints.

Phase 2 changes:
  - ChatResponse gains a `detected_intent` field (Phase 1 didn't have this)
  - OrchestratedChatResponse is the new response model for /chat/v2

Place this file at: backend/api/schemas/ai.py
"""

from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# REQUEST MODEL (unchanged from Phase 1)
# =============================================================================

class ChatRequest(BaseModel):
    """
    What the client sends to /api/v1/ai/chat and /api/v1/ai/chat/v2

    Example:
        {
            "question": "Which skills are growing fastest in 2024?",
            "context": "workforce analytics"
        }
    """
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="The user's natural language question about the job market.",
        examples=["Which skills are growing fastest in 2024?"],
    )
    context: str = Field(
        default="global job market and workforce analytics",
        max_length=200,
        description="Optional context hint to focus the AI's answer domain.",
    )


# =============================================================================
# PHASE 1 RESPONSE (kept for backward compatibility — /chat still works)
# =============================================================================

class ChatResponse(BaseModel):
    """
    Response from /api/v1/ai/chat (Phase 1 endpoint — unchanged).
    """
    answer: str = Field(description="The AI-generated answer.")
    model: str = Field(description="The Groq model used.")
    tokens_used: int = Field(description="Total tokens consumed.")
    question: str = Field(description="Echo of the original question.")


# =============================================================================
# PHASE 2 RESPONSE (new — adds detected_intent)
# =============================================================================

class OrchestratedChatResponse(BaseModel):
    """
    Response from /api/v1/ai/chat/v2 (Phase 2 orchestrated endpoint).

    Adds `detected_intent` so the frontend knows what category of question
    was asked. This enables the UI to show context-aware labels, icons,
    and suggested follow-up questions.

    Example:
        {
            "answer": "The fastest growing skills in 2024 are...",
            "model": "llama-3.1-8b-instant",
            "tokens_used": 312,
            "question": "Which skills are growing fastest?",
            "detected_intent": "skills"
        }
    """
    answer: str = Field(description="The AI-generated answer.")
    model: str = Field(description="The Groq model used.")
    tokens_used: int = Field(description="Total tokens consumed.")
    question: str = Field(description="Echo of the original question.")
    detected_intent: str = Field(
        description=(
            "Detected question category: salary | skills | hiring | "
            "ai_disruption | forecast | general"
        )
    )