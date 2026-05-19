"""
api/schemas/analytics.py
========================
Pydantic schemas for the Phase 3 Analytics Engine endpoints.

These cover advanced computations that go beyond simple aggregations:
  • Salary percentile distribution   (maps to 11_percentile_scoring.sql)
  • Rolling trend averages           (maps to 09_rolling_trends.sql)
  • AI adoption vs risk correlation  (maps to 10_correlation_analysis.sql)
  • Skill demand cohort analysis     (maps to 12_cohort_analysis.sql)
"""

from pydantic import BaseModel


# =============================================================================
# Percentile Scoring
# =============================================================================

class SalaryPercentile(BaseModel):
    """
    Salary distribution bands for a single year.
    Lets the frontend show a box-plot or distribution chart.

    p25 = bottom 25% earners threshold
    p50 = median (50th percentile)
    p75 = top 25% earners threshold
    p90 = top 10% earners threshold
    """
    year: int
    p25_salary: float
    p50_salary: float
    p75_salary: float
    p90_salary: float
    avg_salary: float


class RolePercentileScore(BaseModel):
    """
    Where a specific role ranks within the salary distribution.
    Answers: 'Is a Data Engineer salary above average?'
    """
    role_name: str
    seniority_level: str
    avg_salary_usd: float
    salary_percentile_rank: float   # 0.0–1.0 (e.g. 0.85 = top 15%)
    salary_tier: str                # "Top 10%" | "Top 25%" | "Average" | "Below Average"


# =============================================================================
# Rolling Trends
# =============================================================================

class RollingTrendPoint(BaseModel):
    """
    One year's data with a 3-year rolling average overlaid.
    The rolling average smooths out year-to-year noise —
    the same technique used in financial time-series analysis.

    rolling_avg_* is NULL for the first 1–2 years (not enough history yet).
    """
    year: int
    total_postings: int
    rolling_avg_postings: float | None
    avg_salary_usd: float | None
    rolling_avg_salary: float | None


# =============================================================================
# Correlation Analysis
# =============================================================================

class AICorrelationPoint(BaseModel):
    """
    One industry's data point on the AI adoption vs disruption scatter chart.
    Answers: 'Do highly AI-adopted industries have higher automation risk?'

    The frontend plots ai_adoption_index (x-axis) vs avg_automation_risk (y-axis)
    with each bubble = one industry, sized by avg_future_safe.
    """
    industry_name: str
    sector: str
    ai_adoption_index: float        # from dim_industry (0–100)
    avg_automation_risk: float | None   # from fact_ai_disruption
    avg_future_safe: float | None       # from fact_ai_disruption
    role_count: int                 # how many roles in this industry


# =============================================================================
# Cohort Analysis
# =============================================================================

class SkillCohort(BaseModel):
    """
    A skill grouped by the year it first crossed the 'high demand' threshold.
    Cohort = a group of skills that emerged together.

    Answers: 'Which skills emerged in 2020 and kept growing since?'
    This is the same cohort technique used to analyse user retention in products.
    """
    skill_name: str
    skill_category: str
    is_ai_related: bool
    first_high_demand_year: int     # first year demand_score crossed threshold
    peak_demand_score: float        # highest demand_score ever recorded
    growth_pct: float | None        # CANONICAL KPI from dim_skill


class CohortSummary(BaseModel):
    """
    Aggregated summary per cohort year — how many skills emerged and their avg growth.
    Powers the cohort heatmap or timeline bar chart.
    """
    cohort_year: int
    skill_count: int
    ai_skill_count: int
    avg_growth_pct: float | None
    avg_peak_demand: float | None