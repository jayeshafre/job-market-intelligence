"""
api/schemas/ml.py
=================
Pydantic schemas for the ML/Forecasting/Anomaly Detection layer — Phase 8.

Kept separate from schemas/ai.py intentionally:
  - ai.py   = AI assistant schemas (chat, memory, summaries, alerts)
  - ml.py   = ML model schemas (forecasts, predictions, anomalies)

Clean separation of concerns — matches how real ML platforms are structured.

Place this file at: backend/api/schemas/ml.py
"""

from pydantic import BaseModel, Field


# =============================================================================
# FORECASTING SCHEMAS
# =============================================================================

class ForecastPoint(BaseModel):
    """A single point in a time-series forecast."""
    year:           int
    predicted_value: float = Field(description="The forecasted value for this year.")
    lower_bound:    float  = Field(description="80% confidence interval lower bound.")
    upper_bound:    float  = Field(description="80% confidence interval upper bound.")
    is_forecast:    bool   = Field(description="True if this is a future prediction, False if historical fit.")


class HiringForecastResponse(BaseModel):
    """
    Response from GET /api/v1/ml/forecast/hiring

    historical: Fitted values for 2018–2024 (what Prophet learned).
    forecast:   Predicted values for 2025–2026.
    model_used: Always 'prophet' for this endpoint.
    """
    historical:      list[ForecastPoint]
    forecast:        list[ForecastPoint]
    model_used:      str = Field(default="prophet")
    periods_ahead:   int = Field(description="How many years ahead were forecast.")
    trained_on_years: int = Field(description="Number of historical years used for training.")


class SalaryForecastResponse(BaseModel):
    """Response from GET /api/v1/ml/forecast/salary"""
    historical:       list[ForecastPoint]
    forecast:         list[ForecastPoint]
    model_used:       str = Field(default="prophet")
    periods_ahead:    int
    trained_on_years: int


# =============================================================================
# SALARY PREDICTION SCHEMAS
# =============================================================================

class SalaryPredictionRequest(BaseModel):
    """
    Input features for the XGBoost salary prediction model.

    These are the same features available in your warehouse:
      role_category, seniority_level → from dim_job_role
      region                         → from dim_country
      year                           → target prediction year
    """
    role_category:   str = Field(
        description="Role category from dim_job_role.",
        examples=["Engineering", "Analytics", "Management", "Healthcare"],
    )
    seniority_level: str = Field(
        description="Seniority level from dim_job_role.",
        examples=["Junior", "Mid", "Senior", "Director", "C-Suite"],
    )
    region:          str = Field(
        description="Geographic region from dim_country.",
        examples=["North America", "Europe", "Asia Pacific", "Middle East"],
    )
    year:            int = Field(
        default=2024, ge=2018, le=2026,
        description="Target year for salary prediction.",
    )


class SalaryPredictionResponse(BaseModel):
    """Response from POST /api/v1/ml/predict/salary"""
    predicted_salary_usd: float = Field(description="XGBoost predicted salary in USD.")
    input_features:       dict  = Field(description="The features used for this prediction.")
    model_used:           str   = Field(default="xgboost")
    model_trained:        bool  = Field(description="True if model was already trained, False if just trained now.")
    confidence_note:      str   = Field(
        description="Reminder that this is a prediction, not a guarantee."
    )


# =============================================================================
# ANOMALY DETECTION SCHEMAS
# =============================================================================

class SalaryAnomaly(BaseModel):
    """A detected salary anomaly for a specific role and year."""
    role_name:        str
    year:             int
    avg_salary_usd:   float
    expected_salary:  float  = Field(description="The mean salary across all years for this role.")
    z_score:          float  = Field(description="Standard deviations from the mean. |z| > 2.0 = anomaly.")
    deviation_pct:    float  = Field(description="Percentage deviation from expected salary.")
    anomaly_type:     str    = Field(description="spike | drop")


class SkillAnomaly(BaseModel):
    """A detected demand anomaly for a specific skill and year."""
    skill_name:       str
    year:             int
    avg_demand_score: float
    expected_demand:  float
    z_score:          float
    deviation_pct:    float
    anomaly_type:     str    = Field(description="spike | drop")


class AnomalyDetectionResponse(BaseModel):
    """
    Response from GET /api/v1/ml/anomalies

    salary_anomalies: Roles with statistically unusual salary in a given year.
    skill_anomalies:  Skills with statistically unusual demand in a given year.
    z_score_threshold: The threshold used (default 2.0).
    total_anomalies:  Combined count of all detected anomalies.
    """
    salary_anomalies:  list[SalaryAnomaly]
    skill_anomalies:   list[SkillAnomaly]
    z_score_threshold: float
    total_anomalies:   int
    year_analyzed:     int