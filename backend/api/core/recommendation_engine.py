"""
api/core/recommendation_engine.py
==================================
Recommendation Engine — Phase 4.

This module takes the detected intent + KPI context and builds a
structured recommendation prompt that instructs Groq to return
actionable, typed recommendations alongside its answer.

Why structured recommendations?
  A plain text answer is great for reading.
  Structured recommendations are great for the frontend to render as
  cards, action items, leaderboards, and guided next steps.

  This is how real analytics platforms work:
    • LinkedIn "Jobs you may like"
    • Coursera "Skills to learn next"
    • Glassdoor "Roles that match your profile"

  We're building the same pattern — powered by your warehouse data.

How it works:
  1. build_recommendation_prompt(intent, kpi_context) builds a special
     instruction block telling Groq to return JSON recommendations.
  2. The service layer appends this to the enriched system prompt.
  3. Groq returns its answer + a JSON block with recommendations.
  4. parse_recommendations() extracts and validates the JSON.
  5. The router returns both the text answer and structured recs.

Recommendation types by intent:
  SALARY        → top roles to target for salary growth
  SKILLS        → skills to learn next based on growth trends
  HIRING        → countries/industries to target for job search
  AI_DISRUPTION → career pivots away from high-risk roles
  FORECAST      → emerging roles to prepare for
  GENERAL       → broad platform-aware career suggestions

Place this file at: backend/api/core/recommendation_engine.py
"""

import json
import logging
import re
from dataclasses import dataclass

from api.core.orchestrator import Intent

logger = logging.getLogger(__name__)


# =============================================================================
# RECOMMENDATION SCHEMA (what Groq must return)
# =============================================================================

# This is the JSON structure we instruct Groq to return.
# It's included in every recommendation prompt so Groq knows the exact shape.
RECOMMENDATION_JSON_SCHEMA = """
Return your recommendations as a JSON block at the END of your response.
The JSON block must follow this EXACT format — no deviations:

```json
{
  "recommendations": [
    {
      "title": "Short action-oriented title (max 8 words)",
      "category": "one of: role | skill | country | industry | career_pivot",
      "rationale": "1-2 sentences explaining why this is recommended",
      "priority": "high | medium | low",
      "estimated_impact": "quantified impact if possible (e.g. +23% salary, top 10% demand)"
    }
  ]
}
```

Rules:
- Return exactly 3 recommendations
- Each recommendation must be specific and actionable
- Use real numbers from the platform data provided
- Do NOT add any text after the closing ```
"""


# =============================================================================
# INTENT-SPECIFIC RECOMMENDATION INSTRUCTIONS
# =============================================================================

# Each intent gets a specific instruction about WHAT KIND of recommendations
# to generate. This focuses Groq on the right recommendation category.

RECOMMENDATION_INSTRUCTIONS: dict[Intent, str] = {

    Intent.SALARY: """
Generate 3 SALARY OPTIMIZATION recommendations.
Focus on: roles to target for higher pay, countries with salary premiums,
seniority paths that unlock the biggest salary jumps.
Use the salary data provided to ground every recommendation in real numbers.
""",

    Intent.SKILLS: """
Generate 3 SKILL INVESTMENT recommendations.
Focus on: the highest-ROI skills to learn next, AI skills with breakout growth,
skill combinations that command salary premiums.
Prioritize skills with growth > 50% from the platform data.
""",

    Intent.HIRING: """
Generate 3 JOB SEARCH STRATEGY recommendations.
Focus on: best countries/regions to target, industries with highest hiring velocity,
roles with the best posting volume + salary combination.
Ground each recommendation in the hiring data provided.
""",

    Intent.AI_DISRUPTION: """
Generate 3 CAREER RESILIENCE recommendations.
Focus on: pivoting away from high-automation-risk roles,
skills that increase future-safe scores, industries with low disruption risk.
Use the automation risk scores from the platform data.
""",

    Intent.FORECAST: """
Generate 3 FUTURE-PROOFING recommendations.
Focus on: emerging roles to prepare for now, skills with accelerating adoption curves,
industries positioned for growth in the next 2-3 years.
Frame each recommendation as a forward-looking action.
""",

    Intent.GENERAL: """
Generate 3 CAREER INTELLIGENCE recommendations.
Pick the highest-impact insights from the platform data provided.
Cover at least 2 different areas (salary, skills, hiring, or AI risk).
Make each recommendation immediately actionable.
""",
}


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_recommendation_prompt(intent: Intent, kpi_context: str) -> str:
    """
    Builds the recommendation instruction block to append to the system prompt.

    This tells Groq:
      1. What type of recommendations to generate (intent-specific)
      2. The exact JSON format to return them in
      3. That it must use real numbers from the KPI context

    Args:
        intent:      The detected intent from the orchestrator.
        kpi_context: The formatted KPI string from Phase 3.

    Returns:
        A string to append to the enriched system prompt.
    """
    instruction = RECOMMENDATION_INSTRUCTIONS.get(
        intent, RECOMMENDATION_INSTRUCTIONS[Intent.GENERAL]
    )

    return f"""
=== RECOMMENDATION ENGINE INSTRUCTIONS ===

After answering the user's question, generate structured recommendations.

{instruction.strip()}

{RECOMMENDATION_JSON_SCHEMA.strip()}
"""


# =============================================================================
# RECOMMENDATION PARSER
# =============================================================================

@dataclass
class ParsedRecommendations:
    """
    Result of parsing Groq's response for recommendations.

    attributes:
        clean_answer:    The text answer with the JSON block removed.
        recommendations: List of recommendation dicts (may be empty on parse failure).
        parse_success:   True if JSON was found and parsed successfully.
    """
    clean_answer: str
    recommendations: list[dict]
    parse_success: bool


def parse_recommendations(raw_answer: str) -> ParsedRecommendations:
    """
    Extracts the JSON recommendations block from Groq's raw response.

    Groq returns:
      [text answer]
      ```json
      { "recommendations": [...] }
      ```

    We split on the ```json marker, parse the JSON, and return:
      - clean_answer: just the text part (no JSON clutter)
      - recommendations: the parsed list

    Graceful degradation:
      If parsing fails for any reason (malformed JSON, missing block, etc.)
      we return the full raw answer as clean_answer and an empty list.
      The endpoint still works — it just has no structured recommendations.

    Args:
        raw_answer: The full string returned by Groq.

    Returns:
        ParsedRecommendations dataclass.
    """
    try:
        # Find the ```json ... ``` block using regex
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, raw_answer, re.DOTALL)

        if not match:
            logger.warning("[REC] No JSON block found in Groq response.")
            return ParsedRecommendations(
                clean_answer=raw_answer.strip(),
                recommendations=[],
                parse_success=False,
            )

        json_str = match.group(1).strip()
        parsed = json.loads(json_str)
        recommendations = parsed.get("recommendations", [])

        # Remove the JSON block from the answer text
        clean_answer = raw_answer[:match.start()].strip()

        logger.info(f"[REC] Parsed {len(recommendations)} recommendations successfully.")
        return ParsedRecommendations(
            clean_answer=clean_answer,
            recommendations=recommendations,
            parse_success=True,
        )

    except json.JSONDecodeError as e:
        logger.warning(f"[REC] JSON parse failed: {e}")
        return ParsedRecommendations(
            clean_answer=raw_answer.strip(),
            recommendations=[],
            parse_success=False,
        )

    except Exception as e:
        logger.warning(f"[REC] Unexpected parse error: {e}")
        return ParsedRecommendations(
            clean_answer=raw_answer.strip(),
            recommendations=[],
            parse_success=False,
        )