"""
api/schemas/ai.py
=================
Pydantic request and response models for the AI chat endpoint.

Why do we define these separately?
  1. FastAPI uses them to auto-generate Swagger documentation.
  2. They validate incoming data before it reaches the service layer.
  3. They give us a clean contract — frontend knows exactly what to send/expect.

Place this file at: backend/api/schemas/ai.py
"""

from pydantic import BaseModel, Field


# =============================================================================
# REQUEST MODEL
# =============================================================================

class ChatRequest(BaseModel):
    """
    What the client sends to /api/v1/ai/chat

    Example request body:
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
# RESPONSE MODEL
# =============================================================================

class ChatResponse(BaseModel):
    """
    What the API returns from /api/v1/ai/chat

    Example response:
        {
            "answer": "The fastest growing skills in 2024 are...",
            "model": "llama-3.1-8b-instant",
            "tokens_used": 312,
            "question": "Which skills are growing fastest in 2024?"
        }
    """

    answer: str = Field(description="The AI-generated answer to the question.")
    model: str = Field(description="The Groq model that generated the answer.")
    tokens_used: int = Field(description="Total tokens consumed (prompt + completion).")
    question: str = Field(description="Echo of the original question for traceability.")