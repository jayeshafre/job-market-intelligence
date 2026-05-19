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
from sqlalchemy.orm import Session
from api.core.kpi_context import build_kpi_context
from api.core.recommendation_engine import (
        build_recommendation_prompt,
        parse_recommendations,
)
 
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
    
def kpi_enriched_ask(question: str, context: str, db) -> dict:
    """
    Phase 3 function — injects real KPI data from the database into the prompt.
 
    What's different from orchestrated_ask():
      1. Calls orchestrate() to detect intent (same as Phase 2)
      2. Calls build_kpi_context(intent, db) to query REAL database KPIs
      3. Appends the KPI block to the system prompt before calling Groq
      4. Returns kpi_context_used=True/False so the frontend can show a badge
 
    This is the most impactful change in the entire AI layer so far:
      Phase 1: generic LLM answer
      Phase 2: intent-focused LLM answer
      Phase 3: intent-focused LLM answer + grounded in your actual data
 
    Args:
        question: The user's question.
        context:  Optional domain context.
        db:       SQLAlchemy Session — needed to query the warehouse.
 
    Returns:
        dict with keys: answer, model, tokens_used, question,
                        detected_intent, kpi_context_used
    """
    from api.core.kpi_context import build_kpi_context
    from api.core.orchestrator import orchestrate
 
    client = get_groq_client()
    model  = get_groq_model()
 
    # Step 1: Detect intent + get intent-specific system prompt
    result = orchestrate(question=question, context=context)
 
    # Step 2: Build real KPI context from the database
    kpi_block = build_kpi_context(intent=result.detected_intent, db=db)
    kpi_context_used = bool(kpi_block)
 
    # Step 3: Inject KPI data into the system prompt
    # The system prompt = intent-specific expert persona + real platform data
    # This is what transforms a generic LLM into a platform-aware analyst.
    if kpi_block:
        enriched_system_prompt = (
            result.system_prompt
            + "\n\n"
            + kpi_block
        )
    else:
        # Graceful fallback — if DB query fails, still answer without data
        enriched_system_prompt = result.system_prompt
 
    logger.info(
        f"[AI] kpi_enriched_ask() | intent={result.detected_intent.value} | "
        f"kpi_injected={kpi_context_used} | model={model}"
    )
 
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enriched_system_prompt},
                {"role": "user",   "content": result.user_message},
            ],
            temperature=0.3,
            max_tokens=900,   # slightly more room for data-rich answers
        )
 
        answer      = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
 
        logger.info(
            f"[AI] kpi_enriched_ask() done | intent={result.detected_intent.value} | "
            f"tokens={tokens_used}"
        )
 
        return {
            "answer":            answer,
            "model":             model,
            "tokens_used":       tokens_used,
            "question":          question,
            "detected_intent":   result.detected_intent.value,
            "kpi_context_used":  kpi_context_used,
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
    
def recommendation_ask(question: str, context: str, db) -> dict:
    """
    Phase 4 function — generates a text answer + structured recommendations.
 
    Build order:
      1. Detect intent (orchestrator)
      2. Fetch real KPIs (Phase 3 kpi_context builder)
      3. Build recommendation instructions (Phase 4 engine)
      4. Combine: intent prompt + KPI data + recommendation instructions
      5. Call Groq with the fully enriched prompt
      6. Parse the JSON recommendations out of the response
      7. Return text answer + structured recommendations separately
 
    The magic is in step 4: the system prompt is now THREE layers deep:
      Layer 1: Expert persona (intent-specific, from Phase 2)
      Layer 2: Real KPI data from your warehouse (Phase 3)
      Layer 3: Recommendation format instructions (Phase 4)
 
    Args:
        question: The user's question.
        context:  Optional domain context.
        db:       SQLAlchemy Session for KPI queries.
 
    Returns:
        dict with keys: answer, model, tokens_used, question,
                        detected_intent, kpi_context_used,
                        recommendations, recommendations_parsed
    """
    from api.core.kpi_context import build_kpi_context
    from api.core.orchestrator import orchestrate
    from api.core.recommendation_engine import (
        build_recommendation_prompt,
        parse_recommendations,
    )
 
    client = get_groq_client()
    model  = get_groq_model()
 
    # Step 1: Detect intent + get base system prompt
    result = orchestrate(question=question, context=context)
 
    # Step 2: Fetch real KPI data from warehouse
    kpi_block = build_kpi_context(intent=result.detected_intent, db=db)
    kpi_context_used = bool(kpi_block)
 
    # Step 3: Build recommendation instructions for this intent
    rec_prompt = build_recommendation_prompt(
        intent=result.detected_intent,
        kpi_context=kpi_block,
    )
 
    # Step 4: Assemble the fully enriched system prompt
    # This is the most powerful prompt in the entire system so far.
    # Three layers: expert persona + real data + structured output instructions
    system_prompt_parts = [result.system_prompt]
    if kpi_block:
        system_prompt_parts.append(kpi_block)
    system_prompt_parts.append(rec_prompt)
 
    enriched_system_prompt = "\n\n".join(system_prompt_parts)
 
    logger.info(
        f"[AI] recommendation_ask() | intent={result.detected_intent.value} | "
        f"kpi_injected={kpi_context_used} | model={model}"
    )
 
    try:
        # Step 5: Call Groq — needs more tokens because response includes JSON
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enriched_system_prompt},
                {"role": "user",   "content": result.user_message},
            ],
            temperature=0.3,
            max_tokens=1200,  # more room: answer text + JSON recommendations block
        )
 
        raw_answer  = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
 
        # Step 6: Parse the JSON recommendations out of the raw response
        parsed = parse_recommendations(raw_answer)
 
        logger.info(
            f"[AI] recommendation_ask() done | intent={result.detected_intent.value} | "
            f"tokens={tokens_used} | recs_parsed={parsed.parse_success} | "
            f"rec_count={len(parsed.recommendations)}"
        )
 
        # Step 7: Return structured result
        return {
            "answer":                  parsed.clean_answer,
            "model":                   model,
            "tokens_used":             tokens_used,
            "question":                question,
            "detected_intent":         result.detected_intent.value,
            "kpi_context_used":        kpi_context_used,
            "recommendations":         parsed.recommendations,
            "recommendations_parsed":  parsed.parse_success,
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
 