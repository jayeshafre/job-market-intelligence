"""
api/services/ai_impact.py
=========================
Database query functions for AI Impact Analytics.

KPI field names used here are CANONICAL — they must match warehouse_schema.sql:
  automation_risk_score, ai_replacement_index, future_safe_score

Tables used: fact_ai_disruption, dim_job_role, dim_industry
"""

from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session

from api.models import DimIndustry, DimJobRole, FactAiDisruption


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


# =============================================================================
# 1. Disruption Scores by Role
# =============================================================================

def get_disruption_scores(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    AI disruption metrics averaged per job role for a given year.
    Sorted by automation risk descending (most at-risk roles first).
    Powers the "Disruption Risk by Role" bar chart.
    """
    stmt = (
        select(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
            func.round(func.avg(FactAiDisruption.automation_risk_score), 2).label("avg_automation_risk"),
            func.round(func.avg(FactAiDisruption.ai_replacement_index), 2).label("avg_ai_replacement"),
            func.round(func.avg(FactAiDisruption.future_safe_score), 2).label("avg_future_safe"),
        )
        .join(DimJobRole, FactAiDisruption.role_id == DimJobRole.role_id)
        .where(FactAiDisruption.year == year)
        .group_by(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
        )
        .order_by(desc("avg_automation_risk"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 2. Future-Safe Careers
# =============================================================================

def get_future_safe_careers(
    db: Session,
    year: int = 2024,
    limit: int = 10,
) -> list[dict]:
    """
    Top N careers ranked by future_safe_score (highest = safest from AI).
    Also includes the role-level ai_disruption_risk baseline from dim_job_role.
    Powers the "Safest Careers from AI" leaderboard.

    Why two risk fields?
      ai_disruption_risk  (dim_job_role) = structural baseline for the role
      future_safe_score   (fact_ai_disruption) = time-series computed signal
    """
    stmt = (
        select(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.ai_disruption_risk,   # role-level baseline
            DimJobRole.is_remote_eligible,
            func.round(func.avg(FactAiDisruption.future_safe_score), 2).label("avg_future_safe_score"),
        )
        .join(DimJobRole, FactAiDisruption.role_id == DimJobRole.role_id)
        .where(FactAiDisruption.year == year)
        .group_by(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.ai_disruption_risk,
            DimJobRole.is_remote_eligible,
        )
        .order_by(desc("avg_future_safe_score"))
        .limit(limit)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


# =============================================================================
# 3. AI Disruption by Industry
# =============================================================================

def get_disruption_by_industry(
    db: Session,
    year: int = 2024,
) -> list[dict]:
    """
    AI disruption averaged per industry, sorted by automation risk.
    Answers: "Which industries face the most AI disruption?"
    Powers the industry disruption comparison chart.
    """
    stmt = (
        select(
            DimIndustry.industry_name,
            DimIndustry.sector,
            DimIndustry.ai_adoption_index,
            func.round(func.avg(FactAiDisruption.automation_risk_score), 2).label("avg_automation_risk"),
            func.round(func.avg(FactAiDisruption.future_safe_score), 2).label("avg_future_safe"),
        )
        .join(DimIndustry, FactAiDisruption.industry_id == DimIndustry.industry_id)
        .where(FactAiDisruption.year == year)
        .group_by(
            DimIndustry.industry_name,
            DimIndustry.sector,
            DimIndustry.ai_adoption_index,
        )
        .order_by(desc("avg_automation_risk"))
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 4. Disruption Trend Over Time
# =============================================================================

def get_disruption_trends(
    db: Session,
    start_year: int = 2018,
    end_year: int = 2024,
) -> list[dict]:
    """
    Global AI disruption trend year over year.
    Answers: "Is automation risk increasing or stabilising over time?"
    Powers the disruption trend line chart.
    """
    stmt = (
        select(
            FactAiDisruption.year,
            func.round(func.avg(FactAiDisruption.automation_risk_score), 2).label("avg_automation_risk"),
            func.round(func.avg(FactAiDisruption.future_safe_score), 2).label("avg_future_safe"),
            func.round(func.avg(FactAiDisruption.ai_replacement_index), 2).label("avg_ai_replacement"),
        )
        .where(FactAiDisruption.year.between(start_year, end_year))
        .group_by(FactAiDisruption.year)
        .order_by(FactAiDisruption.year)
    )
    return _rows_to_dicts(db.execute(stmt).all())