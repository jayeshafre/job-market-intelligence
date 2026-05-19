"""
api/services/ai.py
==================
AI service layer — handles Groq API calls for the chat endpoint.

This is where all the AI logic lives. The router stays thin (HTTP only).
The service handles:
  1. Building the system prompt (makes Groq act like an analytics expert)
  2. Calling the Groq API
  3. Extracting and returning the response

Why a system prompt?
  A system prompt is like the job description you give to an employee before
  they start. It tells the LLM: "You are an expert in X. You answer like Y.
  You never do Z." Without it, the LLM answers generically. With it, every
  answer is focused on job market analytics.

Place this file at: backend/api/services/ai.py
"""

import logging

from groq import APIConnectionError, APIStatusError, RateLimitError

from api.core.groq_client import get_groq_client, get_groq_model

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

# This is the "personality" of your AI assistant.
# Think of it as the instructions you give to a new analyst on day one.
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
# SERVICE FUNCTION
# =============================================================================

def ask_groq(question: str, context: str) -> dict:
    """
    Sends a question to Groq and returns a structured response dict.

    Args:
        question: The user's natural language question.
        context:  Optional domain context to include in the user message.

    Returns:
        dict with keys: answer, model, tokens_used, question

    Raises:
        RuntimeError: Wraps Groq API errors with a clean message for the router.
    """
    client = get_groq_client()
    model = get_groq_model()

    # The user message includes both the question and optional context.
    # Giving the model context helps it stay on-topic.
    user_message = f"Context: {context}\n\nQuestion: {question}"

    logger.info(f"[AI] Sending question to Groq model={model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.3,    # Lower = more factual, less creative. Good for analytics.
            max_tokens=800,     # Enough for a thorough answer without being wasteful.
        )

        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        logger.info(f"[AI] Response received. tokens_used={tokens_used}")

        return {
            "answer": answer,
            "model": model,
            "tokens_used": tokens_used,
            "question": question,
        }

    except RateLimitError:
        logger.warning("[AI] Groq rate limit hit.")
        raise RuntimeError(
            "AI service is temporarily rate-limited. Please wait a moment and try again."
        )

    except APIConnectionError:
        logger.error("[AI] Could not connect to Groq API.")
        raise RuntimeError(
            "Could not reach the AI service. Check your internet connection."
        )

    except APIStatusError as e:
        logger.error(f"[AI] Groq API error: {e.status_code} - {e.message}")
        raise RuntimeError(
            f"AI service returned an error (status {e.status_code}). Check your API key."
        )