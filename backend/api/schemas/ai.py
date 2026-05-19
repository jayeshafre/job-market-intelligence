"""
api/schemas/ai.py
=================
Pydantic request and response models for the AI chat endpoints.

Phase 1: ChatRequest, ChatResponse
Phase 2: OrchestratedChatResponse  (adds detected_intent)
Phase 3: KPIEnrichedChatResponse   (adds kpi_context_used flag)

Place this file at: backend/api/schemas/ai.py
"""

from pydantic import BaseModel, Field
from typing import Any


# =============================================================================
# REQUEST (shared across all phases — unchanged)
# =============================================================================

class ChatRequest(BaseModel):
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
# PHASE 1 RESPONSE
# =============================================================================

class ChatResponse(BaseModel):
    answer: str
    model: str
    tokens_used: int
    question: str


# =============================================================================
# PHASE 2 RESPONSE
# =============================================================================

class OrchestratedChatResponse(BaseModel):
    answer: str
    model: str
    tokens_used: int
    question: str
    detected_intent: str = Field(
        description="salary | skills | hiring | ai_disruption | forecast | general"
    )


# =============================================================================
# PHASE 3 RESPONSE (new)
# =============================================================================

class KPIEnrichedChatResponse(BaseModel):
    """
    Response from POST /api/v1/ai/chat/v3

    Adds kpi_context_used so the frontend knows whether real platform data
    was injected into this answer — useful for showing a "Data-backed" badge.
    """
    answer: str
    model: str
    tokens_used: int
    question: str
    detected_intent: str = Field(
        description="salary | skills | hiring | ai_disruption | forecast | general"
    )
    kpi_context_used: bool = Field(
        description="True if real platform KPI data was injected into this answer."
    )

# =============================================================================
# PHASE 4 — RECOMMENDATION SCHEMAS 
# =============================================================================
 
class Recommendation(BaseModel):
    """
    A single structured recommendation from the Recommendation Engine.
 
    These are rendered as cards on the frontend — each has a title,
    rationale, category, priority, and estimated impact.
    """
    title: str = Field(description="Short action-oriented title.")
    category: str = Field(
        description="role | skill | country | industry | career_pivot"
    )
    rationale: str = Field(description="Why this is recommended.")
    priority: str = Field(description="high | medium | low")
    estimated_impact: str = Field(
        description="Quantified impact where possible (e.g. +23% salary)."
    )
 
 
class RecommendationResponse(BaseModel):
    """
    Response from POST /api/v1/ai/chat/v4
 
    Adds a structured `recommendations` list alongside the text answer.
    The frontend renders the answer as text and the recommendations as cards.
    """
    answer: str
    model: str
    tokens_used: int
    question: str
    detected_intent: str
    kpi_context_used: bool
    recommendations: list[Any] = Field(
        default=[],
        description="Structured recommendations list. Empty if parse failed.",
    )
    recommendations_parsed: bool = Field(
        description="True if recommendations were successfully extracted from response."
    )