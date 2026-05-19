"""
api/routers/workforce.py
========================
HTTP route handlers for Workforce Analytics.

Responsibilities (ONLY):
  • Define URL path, HTTP method, query parameters
  • Validate inputs via FastAPI's Query()
  • Call the service layer
  • Wrap result in APIResponse and return

No business logic here. No SQL here.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.workforce import (
    CountryHiringStats,
    HiringTrendPoint,
    IndustryHiringStats,
    RemoteBreakdown,
    TopRole,
)
from api.services import workforce as workforce_service

router = APIRouter()


@router.get(
    "/hiring-trends",
    response_model=APIResponse[list[HiringTrendPoint]],
    summary="Yearly hiring trend",
    description="Total job postings and avg salary per year. Powers the main trend chart.",
)
def hiring_trends(
    start_year: int = Query(default=2018, ge=2018, le=2024, description="Start year (inclusive)"),
    end_year:   int = Query(default=2024, ge=2018, le=2024, description="End year (inclusive)"),
    db: Session = Depends(get_db),
):
    rows = workforce_service.get_hiring_trends(db, start_year, end_year)
    data = [HiringTrendPoint(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/by-country",
    response_model=APIResponse[list[CountryHiringStats]],
    summary="Hiring demand by country",
    description="Top N countries ranked by total job postings for a given year.",
)
def hiring_by_country(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=60),
    db: Session = Depends(get_db),
):
    rows = workforce_service.get_hiring_by_country(db, year, limit)
    data = [CountryHiringStats(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/by-industry",
    response_model=APIResponse[list[IndustryHiringStats]],
    summary="Hiring demand by industry",
    description="Top N industries ranked by total job postings for a given year.",
)
def hiring_by_industry(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=20),
    db: Session = Depends(get_db),
):
    rows = workforce_service.get_hiring_by_industry(db, year, limit)
    data = [IndustryHiringStats(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/remote-stats",
    response_model=APIResponse[RemoteBreakdown],
    summary="Remote vs on-site breakdown",
    description="Total, remote, and on-site posting counts with remote percentage.",
)
def remote_stats(
    year: int = Query(default=2024, ge=2018, le=2024),
    db: Session = Depends(get_db),
):
    data = workforce_service.get_remote_stats(db, year)
    return APIResponse(data=RemoteBreakdown(**data))


@router.get(
    "/top-roles",
    response_model=APIResponse[list[TopRole]],
    summary="Top job roles by posting volume",
    description="Most in-demand job roles for a given year, ranked by posting count.",
)
def top_roles(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows = workforce_service.get_top_roles(db, year, limit)
    data = [TopRole(**r) for r in rows]
    return APIResponse(data=data, count=len(data))