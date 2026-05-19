"""
api/core/kpi_context.py
=======================
KPI Context Builder — Phase 3.

This module bridges your PostgreSQL warehouse and the Groq LLM.
It queries real data from your services layer and formats it as a
structured text block that gets injected into the AI system prompt.

Why does this matter?
  Without this: AI answers from general training knowledge.
  With this:    AI answers from YOUR platform's actual data.

  Example difference:
    Without: "Data Scientists typically earn $90,000–$130,000 USD..."
    With:    "According to your platform data, the avg Data Scientist
              salary in 2024 is $89,724 (60 data points across 30 countries)."

One builder function per intent:
  build_salary_context()        → for Intent.SALARY
  build_skills_context()        → for Intent.SKILLS
  build_hiring_context()        → for Intent.HIRING
  build_ai_disruption_context() → for Intent.AI_DISRUPTION
  build_general_context()       → for Intent.GENERAL / Intent.FORECAST

Entry point:
  build_kpi_context(intent, db) → returns a formatted string

Place this file at: backend/api/core/kpi_context.py
"""

import logging
from sqlalchemy.orm import Session

from api.core.orchestrator import Intent
from api.services import salary as salary_service
from api.services import skills as skills_service
from api.services import workforce as workforce_service
from api.services import ai_impact as ai_impact_service

logger = logging.getLogger(__name__)


# =============================================================================
# SALARY KPI CONTEXT
# =============================================================================

def build_salary_context(db: Session) -> str:
    try:
        top_roles     = salary_service.get_top_paying_roles(db, year=2024, limit=5)
        top_countries = salary_service.get_top_paying_countries(db, year=2024, limit=5)
        trends        = salary_service.get_salary_trends(db, start_year=2022, end_year=2024)

        lines = ["=== REAL PLATFORM DATA: SALARY INTELLIGENCE (2024) ===\n"]

        lines.append("TOP 5 HIGHEST PAYING ROLES:")
        for r in top_roles:
            lines.append(
                f"  {r['rank']}. {r['role_name']} ({r['seniority_level']}) "
                f"— ${r['avg_salary_usd']:,.2f} USD avg"
            )

        lines.append("\nTOP 5 HIGHEST PAYING COUNTRIES:")
        for c in top_countries:
            lines.append(
                f"  {c['rank']}. {c['country_name']} ({c['region']}) "
                f"— ${c['avg_salary_usd']:,.2f} USD avg"
            )

        if trends:
            latest = trends[-1]
            lines.append(
                f"\nGLOBAL SALARY TREND: 2024 avg = ${latest['avg_salary_usd']:,.2f} USD "
                f"(growth: {latest.get('salary_growth_pct', 'N/A')}%)"
            )

        lines.append("\nUse this real data to give precise, data-backed answers.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[KPI] build_salary_context failed: {e}")
        return ""


# =============================================================================
# SKILLS KPI CONTEXT
# =============================================================================

def build_skills_context(db: Session) -> str:
    try:
        top_skills  = skills_service.get_top_growing_skills(db, year=2024, limit=8)
        ai_skills   = skills_service.get_ai_skills(db, year=2024, limit=5)
        by_category = skills_service.get_skills_by_category(db, year=2024)

        lines = ["=== REAL PLATFORM DATA: SKILL INTELLIGENCE (2024) ===\n"]

        lines.append("TOP 8 FASTEST GROWING SKILLS:")
        for s in top_skills:
            ai_tag = " [AI/ML]" if s.get("is_ai_related") else ""
            lines.append(
                f"  • {s['skill_name']}{ai_tag} ({s['skill_category']}) "
                f"— growth: {s['growth_pct']}%, demand score: {s['avg_demand_score']}"
            )

        lines.append("\nTOP AI/ML SKILLS BY DEMAND SCORE:")
        for s in ai_skills:
            lines.append(
                f"  • {s['skill_name']} — demand: {s['avg_demand_score']}, "
                f"mentions: {s['total_mentions']}"
            )

        lines.append("\nSKILL CATEGORY SUMMARY:")
        for cat in by_category:
            lines.append(
                f"  • {cat['skill_category']}: {cat['skill_count']} skills, "
                f"avg growth {cat['avg_growth_pct']}%, "
                f"{cat['ai_skill_count']} AI-related"
            )

        lines.append("\nUse this real data to give precise, data-backed answers.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[KPI] build_skills_context failed: {e}")
        return ""


# =============================================================================
# HIRING KPI CONTEXT
# =============================================================================

def build_hiring_context(db: Session) -> str:
    try:
        trends         = workforce_service.get_hiring_trends(db, start_year=2022, end_year=2024)
        top_countries  = workforce_service.get_hiring_by_country(db, year=2024, limit=5)
        top_industries = workforce_service.get_hiring_by_industry(db, year=2024, limit=5)
        remote         = workforce_service.get_remote_stats(db, year=2024)
        top_roles      = workforce_service.get_top_roles(db, year=2024, limit=5)

        lines = ["=== REAL PLATFORM DATA: WORKFORCE & HIRING ANALYTICS (2024) ===\n"]

        if trends:
            latest = trends[-1]
            lines.append(
                f"GLOBAL HIRING 2024: {latest['total_postings']:,} total postings, "
                f"avg salary ${latest['avg_salary_usd']:,.2f}, "
                f"remote postings: {latest['remote_postings']:,}"
            )

        lines.append("\nTOP 5 HIRING COUNTRIES:")
        for c in top_countries:
            lines.append(f"  • {c['country_name']} ({c['region']}) — {c['total_postings']:,} postings")

        lines.append("\nTOP 5 HIRING INDUSTRIES:")
        for ind in top_industries:
            lines.append(
                f"  • {ind['industry_name']} ({ind['sector']}) "
                f"— {ind['total_postings']:,} postings, AI adoption: {ind['ai_adoption_index']}"
            )

        lines.append("\nTOP 5 IN-DEMAND ROLES:")
        for r in top_roles:
            lines.append(f"  • {r['role_name']} ({r['role_category']}) — {r['total_postings']:,} postings")

        lines.append(
            f"\nREMOTE WORK: {remote['remote_pct']}% of postings are remote "
            f"({remote['remote_postings']:,} of {remote['total_postings']:,})"
        )

        lines.append("\nUse this real data to give precise, data-backed answers.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[KPI] build_hiring_context failed: {e}")
        return ""


# =============================================================================
# AI DISRUPTION KPI CONTEXT
# =============================================================================

def build_ai_disruption_context(db: Session) -> str:
    try:
        at_risk      = ai_impact_service.get_disruption_scores(db, year=2024, limit=5)
        safe_careers = ai_impact_service.get_future_safe_careers(db, year=2024, limit=5)
        by_industry  = ai_impact_service.get_disruption_by_industry(db, year=2024)

        top_disrupted    = by_industry[:5]
        safest_industries = sorted(by_industry, key=lambda x: x["avg_automation_risk"])[:3]

        lines = ["=== REAL PLATFORM DATA: AI DISRUPTION ANALYTICS (2024) ===\n"]

        lines.append("TOP 5 HIGHEST AUTOMATION RISK ROLES:")
        for r in at_risk:
            lines.append(
                f"  • {r['role_name']} ({r['role_category']}) "
                f"— automation risk: {r['avg_automation_risk']}/100, "
                f"future safe score: {r['avg_future_safe']}/100"
            )

        lines.append("\nTOP 5 SAFEST CAREERS FROM AI:")
        for r in safe_careers:
            lines.append(
                f"  {r['rank']}. {r['role_name']} ({r['role_category']}) "
                f"— future safe score: {r['avg_future_safe_score']}/100"
            )

        lines.append("\nMOST AI-DISRUPTED INDUSTRIES:")
        for ind in top_disrupted:
            lines.append(
                f"  • {ind['industry_name']} — avg risk: {ind['avg_automation_risk']}/100, "
                f"AI adoption: {ind['ai_adoption_index']}"
            )

        lines.append("\nLEAST DISRUPTED INDUSTRIES:")
        for ind in safest_industries:
            lines.append(f"  • {ind['industry_name']} — avg risk: {ind['avg_automation_risk']}/100")

        lines.append("\nUse this real data to give precise, data-backed answers.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[KPI] build_ai_disruption_context failed: {e}")
        return ""


# =============================================================================
# GENERAL / FORECAST KPI CONTEXT
# =============================================================================

def build_general_context(db: Session) -> str:
    try:
        trends    = workforce_service.get_hiring_trends(db, start_year=2024, end_year=2024)
        top_skill = skills_service.get_top_growing_skills(db, year=2024, limit=3)
        top_role  = salary_service.get_top_paying_roles(db, year=2024, limit=1)
        safe      = ai_impact_service.get_future_safe_careers(db, year=2024, limit=3)

        lines = ["=== REAL PLATFORM DATA: GLOBAL JOB MARKET SUMMARY (2024) ===\n"]

        if trends:
            t = trends[0]
            lines.append(
                f"HIRING: {t['total_postings']:,} global postings, "
                f"avg salary ${t['avg_salary_usd']:,.2f}"
            )

        if top_skill:
            names = ", ".join(s["skill_name"] for s in top_skill)
            lines.append(f"TOP GROWING SKILLS: {names}")

        if top_role:
            r = top_role[0]
            lines.append(f"HIGHEST PAID ROLE: {r['role_name']} at ${r['avg_salary_usd']:,.2f}")

        if safe:
            names = ", ".join(r["role_name"] for r in safe)
            lines.append(f"SAFEST CAREERS FROM AI: {names}")

        lines.append("\nUse this real data to give precise, data-backed answers.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"[KPI] build_general_context failed: {e}")
        return ""


# =============================================================================
# INTENT → BUILDER MAP + ENTRY POINT
# =============================================================================

_CONTEXT_BUILDERS = {
    Intent.SALARY:        build_salary_context,
    Intent.SKILLS:        build_skills_context,
    Intent.HIRING:        build_hiring_context,
    Intent.AI_DISRUPTION: build_ai_disruption_context,
    Intent.FORECAST:      build_general_context,
    Intent.GENERAL:       build_general_context,
}


def build_kpi_context(intent: Intent, db: Session) -> str:
    """
    Entry point. Selects the right builder for the detected intent,
    runs it, and returns a formatted KPI string for prompt injection.

    Returns "" on failure — AI still responds, just without real data.
    This is called graceful degradation: the system never crashes because
    of a KPI build failure.
    """
    builder = _CONTEXT_BUILDERS.get(intent, build_general_context)
    logger.info(f"[KPI] Building context for intent={intent.value}")
    context = builder(db)

    if context:
        logger.info(f"[KPI] Context built successfully for intent={intent.value}")
    else:
        logger.warning(f"[KPI] Empty context for intent={intent.value}")

    return context