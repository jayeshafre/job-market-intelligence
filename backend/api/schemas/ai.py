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

# =============================================================================
# PHASE 5 — EXECUTIVE SUMMARY SCHEMAS
# =============================================================================
 
class KeyMetrics(BaseModel):
    """
    The headline KPI strip shown at the top of the executive summary page.
    These are the 7 most important numbers from across the platform.
    """
    total_postings:       int   = Field(description="Total global job postings in 2024.")
    global_avg_salary:    float = Field(description="Global average salary USD in 2024.")
    remote_pct:           float = Field(description="Percentage of postings that are remote.")
    fastest_skill:        str   = Field(description="Name of the fastest growing skill.")
    fastest_skill_growth: float = Field(description="YoY growth % of the fastest skill.")
    highest_risk_role:    str   = Field(description="Role with highest automation risk score.")
    safest_career:        str   = Field(description="Role with highest future-safe score.")
 
 
class ExecutiveSummaryResponse(BaseModel):
    """
    Response from GET /api/v1/ai/executive-summary
 
    summary:     The LLM-generated executive briefing prose (250-350 words).
    key_metrics: Structured headline numbers for the frontend KPI strip.
    generated_at: ISO timestamp — shows freshness of the report.
    tokens_used: Groq token consumption for this summary.
    model:       The model that wrote the summary.
    """
    summary:      str         = Field(description="Executive intelligence briefing prose.")
    key_metrics:  KeyMetrics  = Field(description="Headline KPI numbers for the summary page.")
    generated_at: str         = Field(description="ISO 8601 timestamp of generation.")
    tokens_used:  int
    model:        str
 
 
# =============================================================================
# PHASE 5 — SMART ALERT SCHEMAS
# =============================================================================
 
class SmartAlert(BaseModel):
    """
    A single smart alert fired by the threshold scanner.
    Rendered as a notification card on the frontend.
    """
    severity:   str   = Field(description="critical | warning | info")
    category:   str   = Field(description="skill_surge | automation_risk | salary_shift | remote_shift | hiring_surge")
    title:      str   = Field(description="Short alert headline.")
    message:    str   = Field(description="Full alert explanation with data point context.")
    data_point: float = Field(description="The raw number that triggered this alert.")
    entity:     str   = Field(description="The skill / role / industry that triggered the alert.")
 
 
class SmartAlertsResponse(BaseModel):
    """
    Response from GET /api/v1/ai/smart-alerts
 
    alerts:         Full list of fired alerts, sorted critical → warning → info.
    alert_count:    Total alerts fired.
    critical_count: Number of critical severity alerts.
    warning_count:  Number of warning severity alerts.
    info_count:     Number of info severity alerts.
    scanned_at:     ISO timestamp of when the scan ran.
    """
    alerts:         list[SmartAlert] = Field(description="All fired alerts sorted by severity.")
    alert_count:    int
    critical_count: int
    warning_count:  int
    info_count:     int
    scanned_at:     str = Field(description="ISO 8601 timestamp of the scan.")

# =============================================================================
# PHASE 6 — RAG RESPONSE SCHEMA
# =============================================================================
 
class RetrievedChunk(BaseModel):
    """A single document chunk retrieved from ChromaDB."""
    text:        str   = Field(description="The retrieved text chunk.")
    doc_id:      str   = Field(description="Source document identifier.")
    similarity:  float = Field(description="Cosine similarity score (0–1). Higher = more relevant.")
 
 
class RAGChatResponse(BaseModel):
    """
    Response from POST /api/v1/ai/chat/v5
 
    Adds RAG-specific fields:
      retrieved_chunks:  The document chunks injected into the prompt.
      rag_used:          True if ChromaDB returned relevant chunks.
      chunks_retrieved:  How many chunks were retrieved.
    """
    answer:           str               = Field(description="The AI-generated answer.")
    model:            str
    tokens_used:      int
    question:         str
    detected_intent:  str
    kpi_context_used: bool
    rag_used:         bool              = Field(description="True if knowledge base chunks were retrieved.")
    chunks_retrieved: int               = Field(description="Number of document chunks retrieved.")
    retrieved_chunks: list[RetrievedChunk] = Field(
        default=[],
        description="The actual chunks retrieved — useful for debugging and frontend citation.",
    )
    recommendations:         list[Any] = Field(default=[])
    recommendations_parsed:  bool      = Field(default=False)

# =============================================================================
# PHASE 7 — MEMORY SCHEMAS
# =============================================================================
 
class MemoryChatRequest(BaseModel):
    """
    Request for POST /api/v1/ai/chat/v6 (memory-enabled endpoint).
 
    Adds session_id to the standard ChatRequest.
    If session_id is None, a new session is created automatically.
    Pass the returned session_id in all subsequent requests to maintain context.
    """
    question:   str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="The user's question.",
        examples=["Which jobs are safest from AI?"],
    )
    context: str = Field(
        default="global job market and workforce analytics",
        max_length=200,
    )
    session_id: str | None = Field(
        default=None,
        description=(
            "Conversation session ID. Pass None to start a new session. "
            "Reuse the returned session_id to continue the conversation."
        ),
    )
 
 
class MemoryChatResponse(BaseModel):
    """
    Response from POST /api/v1/ai/chat/v6
 
    Adds memory-specific fields:
      session_id:    Use this in your next request to continue the conversation.
      turn_count:    How many turns have happened in this session.
      memory_used:   True if previous conversation history was injected.
      is_new_session: True if this was the first message in the session.
    """
    answer:           str
    model:            str
    tokens_used:      int
    question:         str
    detected_intent:  str
    kpi_context_used: bool
    rag_used:         bool
    chunks_retrieved: int
    recommendations:        list[Any] = Field(default=[])
    recommendations_parsed: bool      = Field(default=False)
    # Memory-specific fields
    session_id:     str  = Field(description="Use this session_id in your next request.")
    turn_count:     int  = Field(description="Number of completed turns in this session.")
    memory_used:    bool = Field(description="True if conversation history was injected.")
    is_new_session: bool = Field(description="True if this was the first message.")

    # =============================================================================
# PHASE 9 — MULTI-AGENT SCHEMAS
# =============================================================================
 
class AgentOutput(BaseModel):
    """Output from a single specialist agent."""
    agent_name: str   = Field(description="Which agent produced this (e.g. SalaryAgent).")
    domain:     str   = Field(description="Domain covered (salary/skills/hiring/ai_disruption/forecast).")
    success:    bool  = Field(description="True if agent completed without error.")
    insights:   list[str] = Field(default=[], description="Key insight strings extracted by the agent.")
    error:      str   = Field(default="", description="Error message if success=False.")
 
 
class MultiAgentResponse(BaseModel):
    """
    Response from POST /api/v1/ai/chat/v7
 
    The most complete AI response in the system.
    Combines outputs from all relevant specialist agents
    synthesized by the Supervisor into one unified answer.
 
    synthesis:       The Groq-written unified answer from all agent insights.
    agent_outputs:   Individual results from each specialist agent.
    execution_plan:  Which agents were selected and why.
    agents_run:      Number of agents that completed successfully.
    agents_failed:   Number of agents that encountered errors.
    tokens_used:     Groq tokens for the synthesis call only.
    model:           The model used for synthesis.
    """
    question:       str
    synthesis:      str             = Field(description="Unified answer synthesized from all agent outputs.")
    agent_outputs:  list[AgentOutput]
    execution_plan: list[str]       = Field(description="List of agent activation decisions.")
    agents_run:     int
    agents_failed:  int
    tokens_used:    int
    model:          str
 
 