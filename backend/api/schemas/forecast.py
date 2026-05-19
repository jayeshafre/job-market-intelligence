"""
api/schemas/forecast.py
=======================
Pydantic schemas for the Phase 3 Forecasting Engine endpoints.

Prophet returns a DataFrame with columns:
  ds          → date
  yhat        → predicted value (best estimate)
  yhat_lower  → lower confidence bound (80% interval by default)
  yhat_upper  → upper confidence bound

We expose both historical fitted values AND future predictions
so the frontend can draw a continuous line that transitions
from solid (historical) to dashed (forecast).
"""

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    """
    One point on a forecast chart.
    is_forecast=False → historical fitted value (solid line)
    is_forecast=True  → future prediction    (dashed line with confidence band)
    """
    year: int
    ds: str                 # ISO date string e.g. "2025-01-01"
    yhat: float             # predicted value
    yhat_lower: float       # lower confidence bound
    yhat_upper: float       # upper confidence bound
    is_forecast: bool


class HiringForecast(BaseModel):
    """
    Full hiring forecast response — historical + future predictions.
    The frontend uses is_forecast to decide solid vs dashed rendering.
    """
    metric: str             # "total_job_postings"
    unit: str               # "postings"
    historical_range: str   # "2018–2024"
    forecast_range: str     # "2025–2026"
    points: list[ForecastPoint]


class SalaryForecast(BaseModel):
    """
    Full salary forecast response.
    role_name is None when forecasting globally (all roles combined).
    """
    metric: str             # "avg_salary_usd"
    unit: str               # "USD"
    role_name: str | None   # None = global forecast
    historical_range: str
    forecast_range: str
    points: list[ForecastPoint]