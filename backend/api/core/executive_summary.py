"""
api/core/executive_summary.py
==============================
Executive Summary Builder — Phase 5.

Queries all 4 KPI domains from the warehouse, assembles a full platform
snapshot, then asks Groq to write a boardroom-ready intelligence briefing.

Why executive summaries matter in real products:
  Every serious analytics platform has a "summary" or "digest" view.
  Bloomberg Terminal has daily market summaries.
  Google Analytics has weekly digest emails.
  Tableau has "Explain Data" auto-insights.

  We're building the same pattern — powered by your warehouse + LLM.

Flow:
  1. build_platform_snapshot(db)  → queries all 4 service domains
  2. format_snapshot_for_prompt() → formats data as readable text
  3. generate_executive_summary() → calls Groq, returns structured result

Place this file at: backend/api/core/executive_summary.py
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.core.groq_client import get_groq_client, get_groq_model
from api.services import salary as salary_service
from api.services import skills as skills_service
from api.services import workforce as workforce_service
from api.services import ai_impact as ai_impact_service
from groq import APIConnectionError, APIStatusError, RateLimitError

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM PROMPT FOR EXECUTIVE SUMMARY
# =============================================================================

EXECUTIVE_SUMMARY_SYSTEM_PROMPT = """You are a Chief Workforce Intelligence Officer
writing a concise executive briefing for C-suite leaders and board members.

Your briefing must:
- Be written in confident, professional executive language
- Lead with the single most important insight from the data
- Cover 4 domains: hiring trends, salary landscape, skill evolution, AI disruption
- Use specific numbers — never vague language like "significantly" without data
- Be scannable — use short paragraphs, one insight per paragraph
- End with a 1-sentence strategic outlook for the next 12 months
- Total length: 250–350 words maximum

Do NOT use bullet points. Write in flowing executive prose.
Do NOT mention the platform or tool — write as if this is a proprietary briefing.
"""


# =============================================================================
# SNAPSHOT BUILDER
# =============================================================================

def build_platform_snapshot(db: Session) -> dict:
    """
    Queries all 4 KPI domains and assembles a unified platform snapshot dict.
    This is the raw data — formatting happens separately.

    Returns a dict with keys: hiring, salary, skills, ai_disruption.
    Each value is a sub-dict of the most important metrics.
    """
    snapshot = {}

    try:
        trends = workforce_service.get_hiring_trends(db, start_year=2023, end_year=2024)
        remote = workforce_service.get_remote_stats(db, year=2024)
        top_industries = workforce_service.get_hiring_by_industry(db, year=2024, limit=3)
        top_countries = workforce_service.get_hiring_by_country(db, year=2024, limit=3)

        latest = trends[-1] if trends else {}
        prev   = trends[-2] if len(trends) > 1 else {}

        hiring_growth = None
        if latest.get("total_postings") and prev.get("total_postings"):
            hiring_growth = round(
                (latest["total_postings"] - prev["total_postings"])
                / prev["total_postings"] * 100, 1
            )

        snapshot["hiring"] = {
            "total_postings_2024":   latest.get("total_postings", 0),
            "avg_salary_usd":        latest.get("avg_salary_usd", 0),
            "remote_pct":            remote.get("remote_pct", 0),
            "yoy_growth_pct":        hiring_growth,
            "top_industries":        [i["industry_name"] for i in top_industries],
            "top_countries":         [c["country_name"] for c in top_countries],
        }
    except Exception as e:
        logger.warning(f"[EXEC] hiring snapshot failed: {e}")
        snapshot["hiring"] = {}

    try:
        top_roles     = salary_service.get_top_paying_roles(db, year=2024, limit=3)
        top_countries = salary_service.get_top_paying_countries(db, year=2024, limit=3)
        trends        = salary_service.get_salary_trends(db, start_year=2023, end_year=2024)

        latest = trends[-1] if trends else {}
        prev   = trends[-2] if len(trends) > 1 else {}

        salary_growth = latest.get("salary_growth_pct") or (
            round(
                (latest["avg_salary_usd"] - prev["avg_salary_usd"])
                / prev["avg_salary_usd"] * 100, 1
            ) if latest.get("avg_salary_usd") and prev.get("avg_salary_usd") else None
        )

        snapshot["salary"] = {
            "global_avg_2024":    latest.get("avg_salary_usd", 0),
            "yoy_growth_pct":     salary_growth,
            "top_paying_roles":   [r["role_name"] for r in top_roles],
            "top_paying_countries": [c["country_name"] for c in top_countries],
            "highest_salary":     top_roles[0]["avg_salary_usd"] if top_roles else 0,
            "highest_role":       top_roles[0]["role_name"] if top_roles else "",
        }
    except Exception as e:
        logger.warning(f"[EXEC] salary snapshot failed: {e}")
        snapshot["salary"] = {}

    try:
        top_skills  = skills_service.get_top_growing_skills(db, year=2024, limit=5)
        ai_skills   = skills_service.get_ai_skills(db, year=2024, limit=3)
        by_category = skills_service.get_skills_by_category(db, year=2024)

        fastest = top_skills[0] if top_skills else {}
        top_ai  = ai_skills[0] if ai_skills else {}
        top_cat = by_category[0] if by_category else {}

        snapshot["skills"] = {
            "fastest_growing_skill":       fastest.get("skill_name", ""),
            "fastest_growth_pct":          fastest.get("growth_pct", 0),
            "top_ai_skill":                top_ai.get("skill_name", ""),
            "top_ai_demand_score":         top_ai.get("avg_demand_score", 0),
            "top_skill_category":          top_cat.get("skill_category", ""),
            "top_category_growth_pct":     top_cat.get("avg_growth_pct", 0),
            "top_5_skills":                [s["skill_name"] for s in top_skills],
        }
    except Exception as e:
        logger.warning(f"[EXEC] skills snapshot failed: {e}")
        snapshot["skills"] = {}

    try:
        at_risk      = ai_impact_service.get_disruption_scores(db, year=2024, limit=3)
        safe_careers = ai_impact_service.get_future_safe_careers(db, year=2024, limit=3)
        by_industry  = ai_impact_service.get_disruption_by_industry(db, year=2024)

        most_at_risk  = at_risk[0] if at_risk else {}
        safest        = safe_careers[0] if safe_careers else {}
        most_disrupted_ind = by_industry[0] if by_industry else {}

        snapshot["ai_disruption"] = {
            "highest_risk_role":         most_at_risk.get("role_name", ""),
            "highest_risk_score":        most_at_risk.get("avg_automation_risk", 0),
            "safest_career":             safest.get("role_name", ""),
            "safest_score":              safest.get("avg_future_safe_score", 0),
            "most_disrupted_industry":   most_disrupted_ind.get("industry_name", ""),
            "industry_risk_score":       most_disrupted_ind.get("avg_automation_risk", 0),
            "safe_careers_top3":         [r["role_name"] for r in safe_careers],
        }
    except Exception as e:
        logger.warning(f"[EXEC] ai_disruption snapshot failed: {e}")
        snapshot["ai_disruption"] = {}

    return snapshot


def format_snapshot_for_prompt(snapshot: dict) -> str:
    """
    Converts the raw snapshot dict into a readable text block for the LLM.
    Structured clearly so Groq can extract specific numbers easily.
    """
    h = snapshot.get("hiring", {})
    s = snapshot.get("salary", {})
    sk = snapshot.get("skills", {})
    ai = snapshot.get("ai_disruption", {})

    lines = ["=== PLATFORM INTELLIGENCE SNAPSHOT — 2024 ===\n"]

    lines.append("HIRING & WORKFORCE:")
    lines.append(f"  Total global postings: {h.get('total_postings_2024', 'N/A'):,}")
    lines.append(f"  YoY hiring growth: {h.get('yoy_growth_pct', 'N/A')}%")
    lines.append(f"  Remote work share: {h.get('remote_pct', 'N/A')}%")
    lines.append(f"  Top hiring industries: {', '.join(h.get('top_industries', []))}")
    lines.append(f"  Top hiring countries: {', '.join(h.get('top_countries', []))}")

    lines.append("\nSALARY LANDSCAPE:")
    lines.append(f"  Global avg salary: ${s.get('global_avg_2024', 0):,.2f} USD")
    lines.append(f"  YoY salary growth: {s.get('yoy_growth_pct', 'N/A')}%")
    lines.append(f"  Highest paid role: {s.get('highest_role', 'N/A')} at ${s.get('highest_salary', 0):,.2f}")
    lines.append(f"  Top paying countries: {', '.join(s.get('top_paying_countries', []))}")

    lines.append("\nSKILL EVOLUTION:")
    lines.append(f"  Fastest growing skill: {sk.get('fastest_growing_skill', 'N/A')} ({sk.get('fastest_growth_pct', 0)}% growth)")
    lines.append(f"  Top AI skill by demand: {sk.get('top_ai_skill', 'N/A')} (score: {sk.get('top_ai_demand_score', 0)})")
    lines.append(f"  Dominant skill category: {sk.get('top_skill_category', 'N/A')} ({sk.get('top_category_growth_pct', 0)}% avg growth)")
    lines.append(f"  Top 5 skills: {', '.join(sk.get('top_5_skills', []))}")

    lines.append("\nAI DISRUPTION:")
    lines.append(f"  Highest automation risk role: {ai.get('highest_risk_role', 'N/A')} (risk score: {ai.get('highest_risk_score', 0)}/100)")
    lines.append(f"  Safest career from AI: {ai.get('safest_career', 'N/A')} (safe score: {ai.get('safest_score', 0)}/100)")
    lines.append(f"  Most disrupted industry: {ai.get('most_disrupted_industry', 'N/A')} (risk: {ai.get('industry_risk_score', 0)}/100)")
    lines.append(f"  Top safe careers: {', '.join(ai.get('safe_careers_top3', []))}")

    return "\n".join(lines)


# =============================================================================
# SUMMARY GENERATOR
# =============================================================================

def generate_executive_summary(db: Session) -> dict:
    """
    Full executive summary generation pipeline.

    Steps:
      1. Build platform snapshot from all 4 KPI domains
      2. Format snapshot as readable text
      3. Call Groq with executive writing instructions
      4. Return summary + raw key_metrics for frontend display

    Returns:
        dict with keys: summary, key_metrics, generated_at, tokens_used, model
    """
    snapshot    = build_platform_snapshot(db)
    prompt_data = format_snapshot_for_prompt(snapshot)

    client = get_groq_client()
    model  = get_groq_model()

    user_message = (
        f"{prompt_data}\n\n"
        "Write an executive intelligence briefing based on this data. "
        "Lead with the single most critical workforce trend. "
        "Cover all 4 domains. End with a 12-month strategic outlook."
    )

    logger.info("[EXEC] Generating executive summary...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXECUTIVE_SUMMARY_SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.4,   # slightly more expressive for executive writing
            max_tokens=600,
        )

        summary     = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        logger.info(f"[EXEC] Summary generated. tokens={tokens_used}")

        # Extract the most important metrics for the frontend header strip
        key_metrics = {
            "total_postings":       snapshot.get("hiring", {}).get("total_postings_2024", 0),
            "global_avg_salary":    snapshot.get("salary", {}).get("global_avg_2024", 0),
            "remote_pct":           snapshot.get("hiring", {}).get("remote_pct", 0),
            "fastest_skill":        snapshot.get("skills", {}).get("fastest_growing_skill", ""),
            "fastest_skill_growth": snapshot.get("skills", {}).get("fastest_growth_pct", 0),
            "highest_risk_role":    snapshot.get("ai_disruption", {}).get("highest_risk_role", ""),
            "safest_career":        snapshot.get("ai_disruption", {}).get("safest_career", ""),
        }

        return {
            "summary":      summary,
            "key_metrics":  key_metrics,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tokens_used":  tokens_used,
            "model":        model,
        }

    except RateLimitError:
        raise RuntimeError("AI service is rate-limited. Please try again shortly.")
    except APIConnectionError:
        raise RuntimeError("Could not reach the AI service.")
    except APIStatusError as e:
        raise RuntimeError(f"AI service error (status {e.status_code}).")