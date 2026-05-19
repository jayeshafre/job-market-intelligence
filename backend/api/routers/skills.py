"""
api/routers/skills.py
=====================
HTTP route handlers for Skill Intelligence.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.skills import (
    AISkill,
    GrowingSkill,
    SkillCategorySummary,
    SkillDemandTrend,
)
from api.services import skills as skills_service

router = APIRouter()


@router.get(
    "/top-growing",
    response_model=APIResponse[list[GrowingSkill]],
    summary="Fastest growing skills",
    description="Top N skills ranked by YoY demand growth %. Optional AI-only filter.",
)
def top_growing_skills(
    year:     int  = Query(default=2024, ge=2018, le=2024),
    limit:    int  = Query(default=15, ge=1, le=60),
    ai_only:  bool = Query(default=False, description="Return only AI/ML related skills"),
    db: Session = Depends(get_db),
):
    rows = skills_service.get_top_growing_skills(db, year, limit, ai_only)
    data = [GrowingSkill(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/ai-skills",
    response_model=APIResponse[list[AISkill]],
    summary="AI and ML skill demand",
    description="All AI-related skills with demand scores and growth, highest demand first.",
)
def ai_skills(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=60),
    db: Session = Depends(get_db),
):
    rows = skills_service.get_ai_skills(db, year, limit)
    data = [AISkill(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/by-category",
    response_model=APIResponse[list[SkillCategorySummary]],
    summary="Skills grouped by category",
    description="Skill demand aggregated by category — count, avg growth, AI skill count.",
)
def skills_by_category(
    year: int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = skills_service.get_skills_by_category(db, year)
    data = [SkillCategorySummary(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/demand-trend",
    response_model=APIResponse[list[SkillDemandTrend]],
    summary="Skill demand trend over time",
    description=(
        "Year-over-year demand trend for a specific skill (case-insensitive name match). "
        "Example: skill_name=Python"
    ),
)
def skill_demand_trend(
    skill_name: str = Query(..., description="Skill name to look up (e.g. Python, SQL, TensorFlow)"),
    start_year: int = Query(default=2018, ge=2018, le=2024),
    end_year:   int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    rows = skills_service.get_skill_demand_trends(db, skill_name, start_year, end_year)
    data = [SkillDemandTrend(**r) for r in rows]
    return APIResponse(data=data, count=len(data))