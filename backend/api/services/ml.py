"""
api/services/ml.py
==================
ML Service Layer — Phase 8.

Three capabilities:
  1. Forecasting       → Exponential Smoothing (statsmodels) — Prophet replacement
  2. Salary Prediction → XGBoost regression model
  3. Anomaly Detection → Z-score statistical analysis

Forecasting note:
  Originally designed for Prophet but replaced with statsmodels
  ExponentialSmoothing (Holt-Winters) for Windows compatibility.
  ETS (Error, Trend, Seasonal) produces equally valid forecasts for
  annual data and requires zero C++ dependencies.

Place this file at: backend/api/services/ml.py
"""

import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import cast, extract, func, Integer, select, text
from sqlalchemy.orm import Session

from api.models import DimJobRole, DimSkill, FactJobPostings, FactSalaryTrends, FactSkillDemand

logger = logging.getLogger(__name__)

# Path where trained XGBoost model is persisted
MODEL_DIR    = Path(__file__).parent.parent.parent / "forecasting" / "models"
MODEL_PATH   = MODEL_DIR / "salary_xgb.pkl"
ENCODER_PATH = MODEL_DIR / "salary_encoders.pkl"


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


# =============================================================================
# SHARED ETS FORECASTER (replaces Prophet)
# =============================================================================

def _forecast_with_ets(
    values:  list[float],
    years:   list[int],
    periods: int,
) -> tuple[list[dict], list[dict]]:
    """
    Exponential Smoothing (Holt-Winters additive trend) forecast.

    Why ETS over Prophet on Windows?
      Prophet requires CmdStan — a C++ binary that needs a separate
      install step and fails silently on many Windows environments.
      statsmodels ETS is pure Python + numpy — zero extra setup,
      works identically on Windows, Mac, and Linux.

    What is Exponential Smoothing?
      It's a weighted average where recent observations get MORE weight
      than older ones. The "trend" component captures whether values
      are going up or down over time.

      Think of it like a moving average that's smart about recency:
        Raw hiring 2023: 700,000
        Raw hiring 2024: 795,000
        ETS says 2025 will be: ~890,000 (continuing the trend)

    Confidence interval:
      We use 1.5× residual standard deviation as the margin.
      The margin widens for further-out predictions (more uncertainty).

    Args:
        values:  Historical values (e.g. total_postings per year).
        years:   Corresponding years (e.g. [2018, 2019, ..., 2024]).
        periods: Number of future years to forecast.

    Returns:
        (historical, forecast) — two lists of ForecastPoint dicts.
    """
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    # Build a pandas Series with a proper DatetimeIndex
    # Prophet used "YS" (year start). We do the same for consistency.
    series = pd.Series(
        values,
        index=pd.date_range(start=str(years[0]), periods=len(years), freq="YS"),
    )

    # Fit Holt's Linear Trend model (additive trend, no seasonality)
    # Annual data has no meaningful intra-year seasonality to model
    model  = ExponentialSmoothing(series, trend="add", seasonal=None)
    fitted = model.fit(optimized=True)

    # Generate forecast
    forecast_series = fitted.forecast(periods)
    fitted_values   = fitted.fittedvalues

    # Confidence interval: residual std × 1.5 (widens with horizon)
    residual_std = float(np.std(fitted.resid))
    base_margin  = residual_std * 1.5

    historical = [
        {
            "year":            y,
            "predicted_value": round(float(fitted_values.iloc[i]), 2),
            "lower_bound":     round(float(fitted_values.iloc[i]) - base_margin, 2),
            "upper_bound":     round(float(fitted_values.iloc[i]) + base_margin, 2),
            "is_forecast":     False,
        }
        for i, y in enumerate(years)
    ]

    forecast = [
        {
            "year":            years[-1] + i + 1,
            "predicted_value": round(float(v), 2),
            # Uncertainty grows with each step ahead
            "lower_bound":     round(float(v) - base_margin * (i + 1), 2),
            "upper_bound":     round(float(v) + base_margin * (i + 1), 2),
            "is_forecast":     True,
        }
        for i, (_, v) in enumerate(forecast_series.items())
    ]

    return historical, forecast


# =============================================================================
# 1. HIRING FORECAST — ETS
# =============================================================================

def forecast_hiring(db: Session, periods: int = 2) -> dict:
    """
    Forecasts future global hiring volumes using Exponential Smoothing.

    Training data: yearly total job postings from fact_job_postings (2018–2024).
    Output: fitted historical values + forecasted values for next `periods` years.

    Args:
        db:      SQLAlchemy session.
        periods: Number of years to forecast ahead (default: 2).

    Returns:
        dict matching HiringForecastResponse schema.
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)
    stmt = (
        select(
            year_col.label("year"),
            func.sum(FactJobPostings.posting_count).label("total_postings"),
        )
        .group_by(year_col)
        .order_by(year_col)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())

    if len(rows) < 3:
        raise RuntimeError("Not enough historical data for forecasting (need at least 3 years).")

    years  = [r["year"] for r in rows]
    values = [float(r["total_postings"]) for r in rows]

    logger.info(f"[ML] Forecasting hiring: {len(years)} historical years → {periods} ahead")

    historical, forecast = _forecast_with_ets(values, years, periods)

    logger.info(
        f"[ML] Hiring forecast complete | "
        f"last_actual={values[-1]:,.0f} | "
        f"next_year_pred={forecast[0]['predicted_value']:,.0f}"
    )

    return {
        "historical":       historical,
        "forecast":         forecast,
        "model_used":       "exponential_smoothing",
        "periods_ahead":    periods,
        "trained_on_years": len(years),
    }


# =============================================================================
# 2. SALARY FORECAST — ETS
# =============================================================================

def forecast_salary(db: Session, periods: int = 2) -> dict:
    """
    Forecasts global average salary trend using Exponential Smoothing.
    Same pattern as forecast_hiring() but uses fact_salary_trends.

    Args:
        db:      SQLAlchemy session.
        periods: Number of years to forecast ahead (default: 2).

    Returns:
        dict matching SalaryForecastResponse schema.
    """
    stmt = (
        select(
            FactSalaryTrends.year,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary"),
        )
        .where(FactSalaryTrends.quarter.is_(None))
        .group_by(FactSalaryTrends.year)
        .order_by(FactSalaryTrends.year)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())

    if len(rows) < 3:
        raise RuntimeError("Not enough salary data for forecasting.")

    years  = [r["year"] for r in rows]
    values = [float(r["avg_salary"]) for r in rows]

    logger.info(f"[ML] Forecasting salary: {len(years)} historical years → {periods} ahead")

    historical, forecast = _forecast_with_ets(values, years, periods)

    logger.info(
        f"[ML] Salary forecast complete | "
        f"last_actual=${values[-1]:,.2f} | "
        f"next_year_pred=${forecast[0]['predicted_value']:,.2f}"
    )

    return {
        "historical":       historical,
        "forecast":         forecast,
        "model_used":       "exponential_smoothing",
        "periods_ahead":    periods,
        "trained_on_years": len(years),
    }


# =============================================================================
# 3. SALARY PREDICTION — XGBoost
# =============================================================================

def _load_training_data(db: Session) -> pd.DataFrame:
    """
    Fetches salary training data from the warehouse.
    Features: role_category, seniority_level, region, year → target: avg_salary_usd
    """
    stmt = text("""
        SELECT
            jr.role_category,
            jr.seniority_level,
            c.region,
            st.year,
            AVG(st.avg_salary_usd) AS avg_salary_usd
        FROM fact_salary_trends st
        JOIN dim_job_role jr ON st.role_id = jr.role_id
        JOIN dim_country  c  ON st.country_id = c.country_id
        WHERE st.quarter IS NULL
        GROUP BY jr.role_category, jr.seniority_level, c.region, st.year
        ORDER BY st.year
    """)
    rows = db.execute(stmt).fetchall()
    return pd.DataFrame(
        rows,
        columns=["role_category", "seniority_level", "region", "year", "avg_salary_usd"],
    )


def train_salary_model(db: Session) -> dict:
    """
    Trains an XGBoost regression model to predict salary from role features.

    Feature engineering:
      Categorical columns (role_category, seniority_level, region) are
      label-encoded to integers — XGBoost requires numeric inputs.

    Model persistence:
      Model + encoders saved to forecasting/models/ with pickle.
      Subsequent calls load from disk — no retraining on every request.

    Returns:
        dict with training summary metrics.
    """
    try:
        import xgboost as xgb
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, r2_score
    except ImportError:
        raise RuntimeError("xgboost or scikit-learn not installed.")

    logger.info("[ML] Training XGBoost salary prediction model...")

    df = _load_training_data(db)
    if df.empty:
        raise RuntimeError("No training data available.")

    # Label encode categoricals
    encoders = {}
    cat_cols  = ["role_category", "seniority_level", "region"]
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    X = df[["role_category", "seniority_level", "region", "year"]]
    y = df["avg_salary_usd"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbosity=0,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae    = round(float(mean_absolute_error(y_test, y_pred)), 2)
    r2     = round(float(r2_score(y_test, y_pred)), 4)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH,    "wb") as f: pickle.dump(model,    f)
    with open(ENCODER_PATH,  "wb") as f: pickle.dump(encoders, f)

    logger.info(f"[ML] XGBoost trained | MAE=${mae:,.2f} | R²={r2} | rows={len(df)}")
    return {
        "status":        "trained",
        "training_rows": len(df),
        "test_mae_usd":  mae,
        "r2_score":      r2,
        "model_path":    str(MODEL_PATH),
    }


def predict_salary(
    db: Session,
    role_category:   str,
    seniority_level: str,
    region:          str,
    year:            int,
) -> dict:
    """
    Predicts salary using the trained XGBoost model.
    Trains automatically on first call if model not yet persisted.
    """
    import xgboost as xgb

    model_trained = MODEL_PATH.exists() and ENCODER_PATH.exists()

    if not model_trained:
        logger.info("[ML] No saved model — training now...")
        train_salary_model(db)

    with open(MODEL_PATH,    "rb") as f: model    = pickle.load(f)
    with open(ENCODER_PATH,  "rb") as f: encoders = pickle.load(f)

    def safe_encode(encoder, value: str) -> int:
        return encoder.transform([value])[0] if value in list(encoder.classes_) else 0

    features = np.array([[
        safe_encode(encoders["role_category"],   role_category),
        safe_encode(encoders["seniority_level"], seniority_level),
        safe_encode(encoders["region"],          region),
        year,
    ]])

    predicted = float(model.predict(features)[0])

    return {
        "predicted_salary_usd": round(predicted, 2),
        "input_features": {
            "role_category":   role_category,
            "seniority_level": seniority_level,
            "region":          region,
            "year":            year,
        },
        "model_used":      "xgboost",
        "model_trained":   model_trained,
        "confidence_note": (
            "This is a statistical prediction based on historical patterns. "
            "Actual salaries vary by company, location specifics, and individual experience."
        ),
    }


# =============================================================================
# 4. ANOMALY DETECTION — Z-Score
# =============================================================================

def detect_salary_anomalies(
    db: Session,
    year: int = 2024,
    z_threshold: float = 2.0,
) -> list[dict]:
    """
    Detects salary anomalies using z-score analysis.

    Z-score = (value - mean) / std_dev

    A role's salary in a given year is anomalous if its z-score
    is more than z_threshold standard deviations from the mean
    across all years for that role.

    |z| > 2.0 → anomaly (outside 95.4% of normal distribution)
    |z| > 3.0 → extreme anomaly (outside 99.7%)
    """
    stmt = text("""
        SELECT
            jr.role_name,
            st.year,
            AVG(st.avg_salary_usd) AS avg_salary_usd
        FROM fact_salary_trends st
        JOIN dim_job_role jr ON st.role_id = jr.role_id
        WHERE st.quarter IS NULL
        GROUP BY jr.role_name, st.year
        ORDER BY jr.role_name, st.year
    """)
    rows = db.execute(stmt).fetchall()
    df = pd.DataFrame(rows, columns=["role_name", "year", "avg_salary_usd"])
    df["avg_salary_usd"] = df["avg_salary_usd"].astype(float)

    if df.empty:
        return []

    # Compute per-role mean and std across all years
    role_stats = (
        df.groupby("role_name")["avg_salary_usd"]
        .agg(["mean", "std"])
        .reset_index()
    )
    role_stats.columns = ["role_name", "role_mean", "role_std"]

    year_df    = df[df["year"] == year].merge(role_stats, on="role_name")
    anomalies  = []

    for _, row in year_df.iterrows():
        if row["role_std"] == 0 or pd.isna(row["role_std"]):
            continue

        z_score = (row["avg_salary_usd"] - row["role_mean"]) / row["role_std"]

        if abs(z_score) >= z_threshold:
            deviation_pct = round(
                (row["avg_salary_usd"] - row["role_mean"]) / row["role_mean"] * 100, 2
            )
            anomalies.append({
                "role_name":       row["role_name"],
                "year":            year,
                "avg_salary_usd":  round(float(row["avg_salary_usd"]), 2),
                "expected_salary": round(float(row["role_mean"]), 2),
                "z_score":         round(float(z_score), 4),
                "deviation_pct":   deviation_pct,
                "anomaly_type":    "spike" if z_score > 0 else "drop",
            })

    anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)
    logger.info(f"[ML] Salary anomalies: {len(anomalies)} detected for year={year}")
    return anomalies


def detect_skill_anomalies(
    db: Session,
    year: int = 2024,
    z_threshold: float = 2.0,
) -> list[dict]:
    """
    Detects skill demand anomalies using the same z-score approach.
    Flags skills with unusually high or low demand in the target year.
    """
    stmt = text("""
        SELECT
            ds.skill_name,
            sd.year,
            AVG(sd.demand_score) AS avg_demand_score
        FROM fact_skill_demand sd
        JOIN dim_skill ds ON sd.skill_id = ds.skill_id
        GROUP BY ds.skill_name, sd.year
        ORDER BY ds.skill_name, sd.year
    """)
    rows = db.execute(stmt).fetchall()
    df = pd.DataFrame(rows, columns=["skill_name", "year", "avg_demand_score"])
    df["avg_demand_score"] = df["avg_demand_score"].astype(float)

    if df.empty:
        return []

    skill_stats = (
        df.groupby("skill_name")["avg_demand_score"]
        .agg(["mean", "std"])
        .reset_index()
    )
    skill_stats.columns = ["skill_name", "skill_mean", "skill_std"]

    year_df   = df[df["year"] == year].merge(skill_stats, on="skill_name")
    anomalies = []

    for _, row in year_df.iterrows():
        if row["skill_std"] == 0 or pd.isna(row["skill_std"]):
            continue

        z_score = (row["avg_demand_score"] - row["skill_mean"]) / row["skill_std"]

        if abs(z_score) >= z_threshold:
            deviation_pct = round(
                (row["avg_demand_score"] - row["skill_mean"]) / row["skill_mean"] * 100, 2
            )
            anomalies.append({
                "skill_name":       row["skill_name"],
                "year":             year,
                "avg_demand_score": round(float(row["avg_demand_score"]), 2),
                "expected_demand":  round(float(row["skill_mean"]), 2),
                "z_score":          round(float(z_score), 4),
                "deviation_pct":    deviation_pct,
                "anomaly_type":     "spike" if z_score > 0 else "drop",
            })

    anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)
    logger.info(f"[ML] Skill anomalies: {len(anomalies)} detected for year={year}")
    return anomalies