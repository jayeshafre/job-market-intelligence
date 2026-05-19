"""
api/routers/forecast.py
=======================
HTTP endpoints for the Phase 3 Forecasting Engine.

Warning to frontend developers:
  Forecast endpoints are slower than analytics endpoints (2–8 seconds)
  because Prophet fits a statistical model on each call.
  Phase 4 will add caching to pre-compute these on a schedule.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import APIResponse
from api.schemas.forecast import HiringForecast, SalaryForecast
from api.services import forecast as forecast_service

router = APIRouter()


@router.get(
    "/hiring",
    response_model=APIResponse[HiringForecast],
    summary="Hiring trend forecast (Prophet)",
    description=(
        "Forecasts global total job postings for the next N years using Meta's Prophet library. "
        "Returns both historical fitted values and future predictions with 80% confidence intervals. "
        "periods: number of years to forecast beyond 2024 (default: 2 → predicts 2025, 2026)."
    ),
)
def hiring_forecast(
    periods: int = Query(default=2, ge=1, le=5, description="Years to forecast beyond 2024"),
    db: Session = Depends(get_db),
):
    result = forecast_service.forecast_hiring(db, periods)
    return APIResponse(data=HiringForecast(**result))


@router.get(
    "/salary",
    response_model=APIResponse[SalaryForecast],
    summary="Salary forecast (Prophet)",
    description=(
        "Forecasts average salary for the next N years. "
        "Without role_id: global forecast across all roles. "
        "With role_id: drill-down forecast for a specific job role."
    ),
)
def salary_forecast(
    periods:  int       = Query(default=2, ge=1, le=5),
    role_id:  int | None = Query(default=None, description="Optional: filter to a specific role ID"),
    db: Session = Depends(get_db),
):
    result = forecast_service.forecast_salary(db, periods, role_id)
    return APIResponse(data=SalaryForecast(**result))