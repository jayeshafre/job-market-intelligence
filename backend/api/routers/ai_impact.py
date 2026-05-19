"""
api/routers/ai_impact.py
========================
HTTP route handlers for AI Impact Analytics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.ai_impact import (
    DisruptionScore,
    DisruptionTrend,
    FutureSafeCareer,
    IndustryDisruption,
)
from api.services import ai_impact as ai_impact_service

router = APIRouter()


@router.get(
    "/disruption-scores",
    response_model=APIResponse[list[DisruptionScore]],
    summary="AI disruption scores by role",
    description="Automation risk, AI replacement index, and future-safe score per job role.",
)
def disruption_scores(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=81),
    db: Session = Depends(get_db),
):
    rows = ai_impact_service.get_disruption_scores(db, year, limit)
    data = [DisruptionScore(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/future-safe-careers",
    response_model=APIResponse[list[FutureSafeCareer]],
    summary="Careers safest from AI disruption",
    description="Top N roles ranked by future_safe_score — highest score = least AI risk.",
)
def future_safe_careers(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows = ai_impact_service.get_future_safe_careers(db, year, limit)
    data = [FutureSafeCareer(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/by-industry",
    response_model=APIResponse[list[IndustryDisruption]],
    summary="AI disruption by industry",
    description="Avg automation risk and future-safe score per industry for a given year.",
)
def disruption_by_industry(
    year: int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = ai_impact_service.get_disruption_by_industry(db, year)
    data = [IndustryDisruption(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/trends",
    response_model=APIResponse[list[DisruptionTrend]],
    summary="AI disruption trend over time",
    description="Global avg automation risk, future-safe score, and AI replacement index year over year.",
)
def disruption_trends(
    start_year: int = Query(default=2018, ge=2018, le=2024),
    end_year:   int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = ai_impact_service.get_disruption_trends(db, start_year, end_year)
    data = [DisruptionTrend(**r) for r in rows]
    return APIResponse(data=data, count=len(data))