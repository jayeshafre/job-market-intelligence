"""
api/routers/salary.py
=====================
HTTP route handlers for Salary Intelligence.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.salary import (
    CountrySalary,
    RoleSalary,
    SalaryTrendPoint,
    TopPayingCountry,
    TopPayingRole,
)
from api.services import salary as salary_service

router = APIRouter()


@router.get(
    "/by-role",
    response_model=APIResponse[list[RoleSalary]],
    summary="Average salary by job role",
    description="Avg salary per role for a given year. Optional seniority filter.",
)
def salary_by_role(
    year:            int       = Query(default=2024, ge=2018, le=2024),
    seniority_level: str | None = Query(default=None, description="Entry | Mid | Senior | Director | C-Suite"),
    limit:           int       = Query(default=20, ge=1, le=81),
    db: Session = Depends(get_db),
):
    rows = salary_service.get_salary_by_role(db, year, seniority_level, limit)
    data = [RoleSalary(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/by-country",
    response_model=APIResponse[list[CountrySalary]],
    summary="Average salary by country",
    description="Avg salary per country for a given year, highest first.",
)
def salary_by_country(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=20, ge=1, le=60),
    db: Session = Depends(get_db),
):
    rows = salary_service.get_salary_by_country(db, year, limit)
    data = [CountrySalary(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/trends",
    response_model=APIResponse[list[SalaryTrendPoint]],
    summary="Salary trend over time",
    description=(
        "Year-over-year avg salary and growth %. "
        "Optional role_id or country_id for drill-down."
    ),
)
def salary_trends(
    start_year: int      = Query(default=2018, ge=2018, le=2024),
    end_year:   int      = Query(default=2024, ge=2018, le=2024),
    role_id:    int | None = Query(default=None, description="Filter by specific role ID"),
    country_id: int | None = Query(default=None, description="Filter by specific country ID"),
    db: Session = Depends(get_db),
):
    rows = salary_service.get_salary_trends(db, start_year, end_year, role_id, country_id)
    data = [SalaryTrendPoint(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/top-paying-roles",
    response_model=APIResponse[list[TopPayingRole]],
    summary="Top paying job roles",
    description="Top N highest-paying roles for a given year with rank numbers.",
)
def top_paying_roles(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows = salary_service.get_top_paying_roles(db, year, limit)
    data = [TopPayingRole(**r) for r in rows]
    return APIResponse(data=data, count=len(data))


@router.get(
    "/top-paying-countries",
    response_model=APIResponse[list[TopPayingCountry]],
    summary="Top paying countries",
    description="Top N highest-paying countries by avg salary for a given year.",
)
def top_paying_countries(
    year:  int = Query(default=2024, ge=2018, le=2024),
    limit: int = Query(default=10, ge=1, le=60),
    db: Session = Depends(get_db),
):
    rows = salary_service.get_top_paying_countries(db, year, limit)
    data = [TopPayingCountry(**r) for r in rows]
    return APIResponse(data=data, count=len(data))