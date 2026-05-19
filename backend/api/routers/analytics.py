"""
api/routers/analytics.py
========================
HTTP endpoints for the Phase 3 Analytics Engine.
Thin layer — all logic is in api/services/analytics.py.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.analytics import (
    AICorrelationPoint,
    CohortSummary,
    RolePercentileScore,
    RollingTrendPoint,
    SalaryPercentile,
    SkillCohort,
)
from api.services import analytics as analytics_service

router = APIRouter()


# =============================================================================
# Percentile Scoring
# =============================================================================

@router.get(
    "/salary-percentiles",
    response_model=APIResponse[list[SalaryPercentile]],
    summary="Salary distribution percentiles by year",
    description=(
        "P25/P50/P75/P90 salary bands for each year. "
        "Uses PostgreSQL PERCENTILE_CONT for true statistical percentiles."
    ),
)
def salary_percentiles(
    start_year: int = Query(default=2018, ge=2018, le=2024),
    end_year:   int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_salary_percentiles(db, start_year, end_year)
    data = [SalaryPercentile(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/role-percentile-scores",
    response_model=APIResponse[list[RolePercentileScore]],
    summary="Where each role ranks in salary distribution",
    description=(
        "PERCENT_RANK() for each job role's salary. "
        "Returns percentile rank (0–1) and a human-readable tier label."
    ),
)
def role_percentile_scores(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=81),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_role_percentile_scores(db, year, limit)
    data = [RolePercentileScore(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


# =============================================================================
# Rolling Trends
# =============================================================================

@router.get(
    "/rolling-trends",
    response_model=APIResponse[list[RollingTrendPoint]],
    summary="N-year rolling average for hiring and salary",
    description=(
        "Smoothed hiring volume and salary using a rolling window average. "
        "Window size is configurable (default: 3 years). "
        "Uses SQL window functions: AVG() OVER (ROWS BETWEEN N PRECEDING AND CURRENT ROW)."
    ),
)
def rolling_trends(
    window: int = Query(default=3, ge=2, le=5, description="Rolling window size in years"),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_rolling_trends(db, window)
    data = [RollingTrendPoint(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


# =============================================================================
# Correlation Analysis
# =============================================================================

@router.get(
    "/ai-correlation",
    response_model=APIResponse[list[AICorrelationPoint]],
    summary="AI adoption vs automation risk by industry",
    description=(
        "Scatter plot dataset: AI adoption index (x) vs avg automation risk (y) per industry. "
        "Answers: do highly AI-adopted industries have more disrupted roles?"
    ),
)
def ai_correlation(
    year: int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_ai_correlation(db, year)
    data = [AICorrelationPoint(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


# =============================================================================
# Cohort Analysis
# =============================================================================

@router.get(
    "/skill-cohorts",
    response_model=APIResponse[list[SkillCohort]],
    summary="Skills grouped by year of high-demand emergence",
    description=(
        "Cohort analysis: groups skills by the first year their demand_score "
        "crossed the threshold. demand_threshold defaults to 65 (out of 100)."
    ),
)
def skill_cohorts(
    demand_threshold: float = Query(
        default=65.0, ge=0.0, le=100.0,
        description="Demand score threshold to qualify as 'high demand'",
    ),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_skill_cohorts(db, demand_threshold)
    data = [SkillCohort(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/cohort-summary",
    response_model=APIResponse[list[CohortSummary]],
    summary="Aggregated cohort metrics per year",
    description=(
        "One row per cohort year: skill count, AI skill count, avg growth, avg peak demand. "
        "Powers the cohort heatmap / timeline chart."
    ),
)
def cohort_summary(
    demand_threshold: float = Query(default=65.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
):
    rows = analytics_service.get_cohort_summary(db, demand_threshold)
    data = [CohortSummary(**r) for r in rows]
    return APIResponse(data=data, count=len(data))