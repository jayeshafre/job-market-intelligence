"""
api/services/forecast.py
========================
Prophet-based forecasting engine — Phase 3.

Prophet is a forecasting library built by Meta's Core Data Science team.
It works well for:
  • Time-series with strong trends       ✓ (salary, hiring always trending)
  • Missing data and outliers            ✓ (our 7-year annual data has neither)
  • Non-linear growth                    ✓ (salary growth is non-linear)

Limitations for this project:
  • Only 7 data points (2018–2024) — short series.
  • Annual granularity — seasonality features are disabled.
  • Confidence intervals will be wide — this is honest, not a bug.

Industry note:
  In production (Meta, Netflix), Prophet runs on 2–5 years of daily data.
  For a portfolio project, 7 annual points still demonstrates the concept
  and produces meaningful directional forecasts.

How to explain this in an interview:
  "I used Prophet for forecasting because it handles trend changes
  (changepoints) automatically, which matters when the hiring market
  changed significantly around 2020 (COVID) and 2022 (tech layoffs)."
"""

import logging
from typing import Any

import pandas as pd
from sqlalchemy import Integer, cast, extract, func, select
from sqlalchemy.orm import Session

from api.models import DimJobRole, FactJobPostings, FactSalaryTrends

logger = logging.getLogger(__name__)


# =============================================================================
# Shared Prophet Config
# =============================================================================

def _build_prophet_model():
    """
    Builds a configured Prophet model suitable for short annual time-series.

    changepoint_prior_scale=0.05:
      Controls how flexible the trend is. Lower = smoother trend.
      Default is 0.05 — we keep it small because with only 7 points
      a highly flexible trend will overfit.

    uncertainty_samples=500:
      Number of Monte Carlo samples for the confidence interval.
      500 is enough for portfolio use; production uses 1000+.
    """
    try:
        from prophet import Prophet
    except ImportError:
        raise RuntimeError(
            "Prophet is not installed. Run: pip install prophet"
        )

    return Prophet(
        yearly_seasonality=False,   # annual data — no sub-year seasonality
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        uncertainty_samples=500,
        interval_width=0.80,        # 80% confidence interval (industry standard)
    )


def _build_future_df(historical_df: pd.DataFrame, periods: int) -> pd.DataFrame:
    """
    Creates the future date DataFrame Prophet needs for prediction.
    Combines historical dates + future year-start dates into one DataFrame.
    """
    last_year = historical_df["ds"].dt.year.max()
    future_dates = pd.date_range(
        start=f"{last_year + 1}-01-01",
        periods=periods,
        freq="YS",   # Year Start — generates Jan 1st of each year
    )
    future_df = pd.DataFrame({"ds": future_dates})
    return pd.concat([historical_df[["ds"]], future_df], ignore_index=True)


def _format_forecast(
    forecast_df: pd.DataFrame,
    historical_years: set[int],
    round_decimals: int = 2,
) -> list[dict]:
    """
    Converts Prophet's output DataFrame into our API format.

    Clamps negative predictions to 0 (hiring/salary can't go negative).
    Marks each point as historical (fitted) or forecast (future).
    """
    points = []
    for _, row in forecast_df.iterrows():
        year = int(row["ds"].year)
        points.append({
            "year": year,
            "ds": row["ds"].strftime("%Y-%m-%d"),
            "yhat":       round(max(0.0, float(row["yhat"])),       round_decimals),
            "yhat_lower": round(max(0.0, float(row["yhat_lower"])), round_decimals),
            "yhat_upper": round(max(0.0, float(row["yhat_upper"])), round_decimals),
            "is_forecast": year not in historical_years,
        })
    return points


# =============================================================================
# 1. Hiring Trend Forecast
# =============================================================================

def forecast_hiring(
    db: Session,
    periods: int = 2,
) -> dict:
    """
    Forecasts total global job postings for the next N years.

    Steps:
      1. Pull yearly total postings from fact_job_postings (2018–2024)
      2. Build Prophet DataFrame (ds=date, y=total_postings)
      3. Fit Prophet model
      4. Predict historical + future periods
      5. Format as list[ForecastPoint]

    periods=2 → forecasts 2025 and 2026.
    """
    # ── 1. Fetch historical data ──────────────────────────────────────────────
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)
    stmt = (
        select(
            year_col.label("year"),
            func.sum(FactJobPostings.posting_count).label("total_postings"),
        )
        .group_by(year_col)
        .order_by(year_col)
    )
    rows = db.execute(stmt).all()

    if not rows:
        return _empty_forecast("total_job_postings", "postings")

    # ── 2. Build Prophet DataFrame ────────────────────────────────────────────
    df = pd.DataFrame([dict(r._mapping) for r in rows])
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    df["y"]  = df["total_postings"].astype(float)
    historical_years = set(df["year"].tolist())

    # ── 3. Fit model ──────────────────────────────────────────────────────────
    try:
        model = _build_prophet_model()
        # Suppress Stan's verbose logging during fitting
        import cmdstanpy  # noqa: F401
        logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
        model.fit(df[["ds", "y"]])
    except Exception as exc:
        logger.error(f"Prophet hiring forecast failed: {exc}")
        return _empty_forecast("total_job_postings", "postings", error=str(exc))

    # ── 4. Predict ────────────────────────────────────────────────────────────
    future_df  = _build_future_df(df, periods)
    forecast   = model.predict(future_df)

    # ── 5. Format ─────────────────────────────────────────────────────────────
    last_hist  = int(df["year"].max())
    last_fcst  = last_hist + periods

    return {
        "metric":           "total_job_postings",
        "unit":             "postings",
        "historical_range": f"2018–{last_hist}",
        "forecast_range":   f"{last_hist + 1}–{last_fcst}",
        "points":           _format_forecast(forecast, historical_years, round_decimals=0),
    }


# =============================================================================
# 2. Salary Forecast
# =============================================================================

def forecast_salary(
    db: Session,
    periods: int = 2,
    role_id: int | None = None,
) -> dict:
    """
    Forecasts average salary for the next N years.
    Optional: drill down to a specific role via role_id.

    Data source: fact_salary_trends (annual, quarter IS NULL)
    """
    # ── 1. Fetch historical data ──────────────────────────────────────────────
    stmt = (
        select(
            FactSalaryTrends.year,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
        )
        .where(FactSalaryTrends.quarter.is_(None))
        .group_by(FactSalaryTrends.year)
        .order_by(FactSalaryTrends.year)
    )

    role_name = None
    if role_id is not None:
        stmt = stmt.where(FactSalaryTrends.role_id == role_id)
        # Fetch role name for the response label
        role_row = db.execute(
            select(DimJobRole.role_name).where(DimJobRole.role_id == role_id)
        ).first()
        role_name = role_row[0] if role_row else f"Role #{role_id}"

    rows = db.execute(stmt).all()

    if not rows:
        return _empty_forecast("avg_salary_usd", "USD", role_name=role_name)

    # ── 2. Build Prophet DataFrame ────────────────────────────────────────────
    df = pd.DataFrame([dict(r._mapping) for r in rows])
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    df["y"]  = df["avg_salary_usd"].astype(float)
    historical_years = set(df["year"].tolist())

    # ── 3. Fit model ──────────────────────────────────────────────────────────
    try:
        model = _build_prophet_model()
        import cmdstanpy  # noqa: F401
        logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
        model.fit(df[["ds", "y"]])
    except Exception as exc:
        logger.error(f"Prophet salary forecast failed: {exc}")
        return _empty_forecast("avg_salary_usd", "USD", role_name=role_name, error=str(exc))

    # ── 4. Predict ────────────────────────────────────────────────────────────
    future_df = _build_future_df(df, periods)
    forecast  = model.predict(future_df)

    # ── 5. Format ─────────────────────────────────────────────────────────────
    last_hist = int(df["year"].max())
    last_fcst = last_hist + periods

    return {
        "metric":           "avg_salary_usd",
        "unit":             "USD",
        "role_name":        role_name,
        "historical_range": f"2018–{last_hist}",
        "forecast_range":   f"{last_hist + 1}–{last_fcst}",
        "points":           _format_forecast(forecast, historical_years, round_decimals=2),
    }


# =============================================================================
# Utility
# =============================================================================

def _empty_forecast(
    metric: str,
    unit: str,
    role_name: str | None = None,
    error: str | None = None,
) -> dict:
    """Returns a safe empty structure when no data is available or Prophet fails."""
    return {
        "metric":           metric,
        "unit":             unit,
        "role_name":        role_name,
        "historical_range": "N/A",
        "forecast_range":   "N/A",
        "points":           [],
        "error":            error,
    }