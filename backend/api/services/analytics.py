"""
api/services/analytics.py
==========================
Advanced analytics query functions — Phase 3 Analytics Engine.

All functions use SQLAlchemy 2.0 and PostgreSQL-specific features:
  • PERCENTILE_CONT  → ordered-set aggregate (requires .within_group())
  • PERCENT_RANK     → window function for relative ranking
  • Rolling AVG      → window function with ROWS BETWEEN frame
  • FILTER clause    → conditional aggregation (PostgreSQL 9.4+)

These patterns mirror the logic in:
  sql/analytics/09_rolling_trends.sql
  sql/analytics/10_correlation_analysis.sql
  sql/analytics/11_percentile_scoring.sql
  sql/analytics/12_cohort_analysis.sql
"""

from sqlalchemy import (
    Integer, String, cast, desc, extract, func, literal, select, text
)
from sqlalchemy.orm import Session

from api.models import (
    DimIndustry, DimJobRole, DimSkill,
    FactAiDisruption, FactJobPostings, FactSalaryTrends, FactSkillDemand,
)


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


# =============================================================================
# 1. Salary Percentile Distribution
# =============================================================================

def get_salary_percentiles(
    db: Session,
    start_year: int = 2018,
    end_year: int = 2024,
) -> list[dict]:
    """
    Computes P25, P50, P75, P90 salary bands for each year.

    Uses PostgreSQL's PERCENTILE_CONT — an "ordered-set aggregate":
      PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY avg_salary_usd)
      = the value at the 50th percentile (true median)

    Why not AVG for median?
      AVG is pulled up by extreme outliers (e.g. a CEO role at $500K).
      PERCENTILE_CONT(0.5) gives the TRUE middle value — much more meaningful.
    """
    stmt = (
        select(
            FactSalaryTrends.year,
            func.round(
                func.percentile_cont(0.25).within_group(FactSalaryTrends.avg_salary_usd), 2
            ).label("p25_salary"),
            func.round(
                func.percentile_cont(0.50).within_group(FactSalaryTrends.avg_salary_usd), 2
            ).label("p50_salary"),
            func.round(
                func.percentile_cont(0.75).within_group(FactSalaryTrends.avg_salary_usd), 2
            ).label("p75_salary"),
            func.round(
                func.percentile_cont(0.90).within_group(FactSalaryTrends.avg_salary_usd), 2
            ).label("p90_salary"),
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary"),
        )
        .where(
            FactSalaryTrends.year.between(start_year, end_year),
            FactSalaryTrends.quarter.is_(None),
        )
        .group_by(FactSalaryTrends.year)
        .order_by(FactSalaryTrends.year)
    )
    return _rows_to_dicts(db.execute(stmt).all())


def get_role_percentile_scores(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    Computes PERCENT_RANK() for each role's salary — shows where it sits
    within the salary distribution (e.g. top 15% of all roles).

    PERCENT_RANK() is a window function:
      0.0 = lowest salary  |  1.0 = highest salary

    salary_tier is a computed label derived from the rank:
      >= 0.90  → "Top 10%"
      >= 0.75  → "Top 25%"
      >= 0.50  → "Above Average"
      else     → "Below Average"
    """
    # Subquery: avg salary per role for the target year
    role_salary_sq = (
        select(
            DimJobRole.role_name,
            DimJobRole.seniority_level,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
        )
        .join(DimJobRole, FactSalaryTrends.role_id == DimJobRole.role_id)
        .where(FactSalaryTrends.year == year)
        .group_by(DimJobRole.role_name, DimJobRole.seniority_level)
        .subquery()
    )

    # Main query: apply PERCENT_RANK window + derive tier label
    pct_rank_col = func.percent_rank().over(
        order_by=role_salary_sq.c.avg_salary_usd
    ).label("salary_percentile_rank")

    stmt = (
        select(
            role_salary_sq.c.role_name,
            role_salary_sq.c.seniority_level,
            role_salary_sq.c.avg_salary_usd,
            pct_rank_col,
        )
        .order_by(desc(role_salary_sq.c.avg_salary_usd))
        .limit(limit)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())

    # Compute tier label in Python (simpler than CASE in SQLAlchemy for beginners)
    for row in rows:
        rank = float(row["salary_percentile_rank"])
        if rank >= 0.90:
            row["salary_tier"] = "Top 10%"
        elif rank >= 0.75:
            row["salary_tier"] = "Top 25%"
        elif rank >= 0.50:
            row["salary_tier"] = "Above Average"
        else:
            row["salary_tier"] = "Below Average"
        # Round to 2 decimal places for clean JSON
        row["salary_percentile_rank"] = round(rank, 4)

    return rows


# =============================================================================
# 2. Rolling Trend Averages
# =============================================================================

def get_rolling_trends(
    db: Session,
    window: int = 3,
) -> list[dict]:
    """
    Computes a N-year rolling average for both hiring volume and salary.

    Rolling average = average of the current year + the N-1 preceding years.
    It smooths out spikes/dips that are noise rather than real signals.

    SQL window function used:
      AVG(total_postings) OVER (
          ORDER BY year
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW   ← 3-year window
      )

    Columns:
      rolling_avg_postings  → NULL for first (window-1) years (not enough history)
      rolling_avg_salary    → same
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    # Step 1: yearly aggregates (subquery)
    yearly_sq = (
        select(
            year_col.label("year"),
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.round(func.avg(FactJobPostings.salary_usd_avg), 2).label("avg_salary_usd"),
        )
        .group_by(year_col)
        .subquery()
    )

    # Step 2: apply rolling window functions over the subquery
    # rows=(-(window-1), 0) means: include (window-1) preceding rows + current row
    frame = (-(window - 1), 0)

    stmt = select(
        yearly_sq.c.year,
        yearly_sq.c.total_postings,
        func.round(
            func.avg(yearly_sq.c.total_postings).over(
                order_by=yearly_sq.c.year,
                rows=frame,
            ), 0
        ).label("rolling_avg_postings"),
        yearly_sq.c.avg_salary_usd,
        func.round(
            func.avg(yearly_sq.c.avg_salary_usd).over(
                order_by=yearly_sq.c.year,
                rows=frame,
            ), 2
        ).label("rolling_avg_salary"),
    ).order_by(yearly_sq.c.year)

    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 3. AI Adoption vs Disruption Correlation
# =============================================================================

def get_ai_correlation(
    db: Session,
    year: int = 2024,
) -> list[dict]:
    """
    For each industry: joins ai_adoption_index (dim_industry) with
    avg automation_risk_score and future_safe_score (fact_ai_disruption).

    The result is a scatter-plot-ready dataset:
      x-axis = ai_adoption_index    (how AI-mature is the industry?)
      y-axis = avg_automation_risk  (how much are its roles at risk?)
      bubble size = avg_future_safe (how safe are its jobs long term?)

    Insight: High AI adoption + High automation risk = disruption hot zone.
    High AI adoption + Low automation risk = AI-augmented (not replaced) industry.
    """
    stmt = (
        select(
            DimIndustry.industry_name,
            DimIndustry.sector,
            DimIndustry.ai_adoption_index,
            func.round(func.avg(FactAiDisruption.automation_risk_score), 2).label("avg_automation_risk"),
            func.round(func.avg(FactAiDisruption.future_safe_score), 2).label("avg_future_safe"),
            func.count(func.distinct(FactAiDisruption.role_id)).label("role_count"),
        )
        .join(DimIndustry, FactAiDisruption.industry_id == DimIndustry.industry_id)
        .where(FactAiDisruption.year == year)
        .group_by(
            DimIndustry.industry_name,
            DimIndustry.sector,
            DimIndustry.ai_adoption_index,
        )
        .order_by(desc(DimIndustry.ai_adoption_index))
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 4. Skill Demand Cohort Analysis
# =============================================================================

def get_skill_cohorts(
    db: Session,
    demand_threshold: float = 65.0,
) -> list[dict]:
    """
    Groups skills into cohorts by the first year they crossed the
    high-demand threshold (demand_score > demand_threshold).

    What is cohort analysis?
      Cohort = a group that shares a common starting event.
      Here: "all skills that first became high-demand in 2020"
      is the 2020 cohort.

    This lets us ask:
      • Did 2020 cohort skills (many AI/cloud tools) grow faster than 2018 cohorts?
      • Which cohort year produced the most durable demand?

    Uses PostgreSQL's FILTER clause (conditional aggregation):
      MIN(year) FILTER (WHERE demand_score > 65)
      = first year the skill exceeded the threshold
    """
    stmt = (
        select(
            DimSkill.skill_name,
            DimSkill.skill_category,
            DimSkill.is_ai_related,
            DimSkill.growth_pct,
            func.min(FactSkillDemand.year).filter(
                FactSkillDemand.demand_score > demand_threshold
            ).label("first_high_demand_year"),
            func.round(
                func.max(FactSkillDemand.demand_score), 2
            ).label("peak_demand_score"),
        )
        .join(DimSkill, FactSkillDemand.skill_id == DimSkill.skill_id)
        .group_by(
            DimSkill.skill_name,
            DimSkill.skill_category,
            DimSkill.is_ai_related,
            DimSkill.growth_pct,
        )
        .having(
            # Only include skills that DID cross the threshold at some point
            func.min(FactSkillDemand.year).filter(
                FactSkillDemand.demand_score > demand_threshold
            ).isnot(None)
        )
        .order_by("first_high_demand_year", desc(DimSkill.growth_pct))
    )
    return _rows_to_dicts(db.execute(stmt).all())


def get_cohort_summary(
    db: Session,
    demand_threshold: float = 65.0,
) -> list[dict]:
    """
    Aggregates get_skill_cohorts() by cohort year.
    Returns one row per year showing how many skills emerged and their avg metrics.

    Powers the cohort timeline / heatmap chart on the dashboard.
    """
    # Use the cohort query as a subquery
    cohort_sq = (
        select(
            DimSkill.skill_name,
            DimSkill.is_ai_related,
            DimSkill.growth_pct,
            func.min(FactSkillDemand.year).filter(
                FactSkillDemand.demand_score > demand_threshold
            ).label("cohort_year"),
            func.round(func.max(FactSkillDemand.demand_score), 2).label("peak_demand_score"),
        )
        .join(DimSkill, FactSkillDemand.skill_id == DimSkill.skill_id)
        .group_by(DimSkill.skill_name, DimSkill.is_ai_related, DimSkill.growth_pct)
        .having(
            func.min(FactSkillDemand.year).filter(
                FactSkillDemand.demand_score > demand_threshold
            ).isnot(None)
        )
        .subquery()
    )

    stmt = (
        select(
            cohort_sq.c.cohort_year,
            func.count(cohort_sq.c.skill_name).label("skill_count"),
            func.sum(
                cast(cohort_sq.c.is_ai_related, Integer)
            ).label("ai_skill_count"),
            func.round(func.avg(cohort_sq.c.growth_pct), 2).label("avg_growth_pct"),
            func.round(func.avg(cohort_sq.c.peak_demand_score), 2).label("avg_peak_demand"),
        )
        .group_by(cohort_sq.c.cohort_year)
        .order_by(cohort_sq.c.cohort_year)
    )
    return _rows_to_dicts(db.execute(stmt).all())