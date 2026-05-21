"""
api/routers/ml.py
=================
HTTP endpoints for the ML/Forecasting/Anomaly Detection layer — Phase 8.

Endpoints:
  GET  /api/v1/ml/forecast/hiring    → Prophet hiring volume forecast
  GET  /api/v1/ml/forecast/salary    → Prophet salary trend forecast
  POST /api/v1/ml/predict/salary     → XGBoost salary prediction
  POST /api/v1/ml/train/salary       → Train/retrain XGBoost model
  GET  /api/v1/ml/anomalies          → Z-score anomaly detection

Place this file at: backend/api/routers/ml.py
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.ml import (
    AnomalyDetectionResponse,
    HiringForecastResponse,
    SalaryAnomaly,
    SalaryForecastResponse,
    SalaryPredictionRequest,
    SalaryPredictionResponse,
    SkillAnomaly,
)
from api.services.ml import (
    detect_salary_anomalies,
    detect_skill_anomalies,
    forecast_hiring,
    forecast_salary,
    predict_salary,
    train_salary_model,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# GET /api/v1/ml/forecast/hiring
# =============================================================================

@router.get(
    "/forecast/hiring",
    response_model=HiringForecastResponse,
    summary="Prophet hiring volume forecast",
    description=(
        "Uses Facebook Prophet to forecast global job posting volumes "
        "for the next 2 years based on 2018–2024 historical data. "
        "Returns historical fitted values + forward predictions with 80% confidence intervals."
    ),
)
def hiring_forecast(
    periods: int = Query(default=2, ge=1, le=5, description="Years to forecast ahead."),
    db: Session = Depends(get_db),
) -> HiringForecastResponse:
    """
    Example response:
        {
            "historical": [
                {"year": 2018, "predicted_value": 82340, "lower_bound": 70000,
                 "upper_bound": 94000, "is_forecast": false},
                ...
            ],
            "forecast": [
                {"year": 2025, "predicted_value": 920000, "lower_bound": 810000,
                 "upper_bound": 1030000, "is_forecast": true},
                {"year": 2026, "predicted_value": 985000, "lower_bound": 860000,
                 "upper_bound": 1110000, "is_forecast": true}
            ],
            "model_used": "prophet",
            "periods_ahead": 2,
            "trained_on_years": 7
        }
    """
    try:
        result = forecast_hiring(db, periods=periods)
        return HiringForecastResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[ML] /forecast/hiring error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in forecasting.")


# =============================================================================
# GET /api/v1/ml/forecast/salary
# =============================================================================

@router.get(
    "/forecast/salary",
    response_model=SalaryForecastResponse,
    summary="Prophet salary trend forecast",
    description=(
        "Forecasts global average salary trend for the next 2 years. "
        "Uses Prophet on annual salary data from fact_salary_trends."
    ),
)
def salary_forecast(
    periods: int = Query(default=2, ge=1, le=5),
    db: Session = Depends(get_db),
) -> SalaryForecastResponse:
    try:
        result = forecast_salary(db, periods=periods)
        return SalaryForecastResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[ML] /forecast/salary error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in forecasting.")


# =============================================================================
# POST /api/v1/ml/predict/salary
# =============================================================================

@router.post(
    "/predict/salary",
    response_model=SalaryPredictionResponse,
    summary="XGBoost salary prediction",
    description=(
        "Predicts salary for a given role_category + seniority_level + region + year "
        "using a trained XGBoost regression model. "
        "Model is trained automatically on first call if not already persisted. "
        "Use POST /ml/train/salary to force a retrain."
    ),
)
def salary_prediction(
    request: SalaryPredictionRequest,
    db: Session = Depends(get_db),
) -> SalaryPredictionResponse:
    """
    Example request:
        { "role_category": "Engineering", "seniority_level": "Senior",
          "region": "North America", "year": 2025 }

    Example response:
        {
            "predicted_salary_usd": 112847.50,
            "input_features": { "role_category": "Engineering", ... },
            "model_used": "xgboost",
            "model_trained": true,
            "confidence_note": "This is a statistical prediction..."
        }
    """
    try:
        result = predict_salary(
            db=db,
            role_category=request.role_category,
            seniority_level=request.seniority_level,
            region=request.region,
            year=request.year,
        )
        return SalaryPredictionResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[ML] /predict/salary error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in prediction.")


# =============================================================================
# POST /api/v1/ml/train/salary
# =============================================================================

@router.post(
    "/train/salary",
    summary="Train or retrain XGBoost salary prediction model",
    description=(
        "Trains the XGBoost salary regression model on all available warehouse data. "
        "Returns MAE and R² metrics. "
        "Model is saved to forecasting/models/salary_xgb.pkl for subsequent predictions."
    ),
)
def train_salary(db: Session = Depends(get_db)) -> dict:
    """
    Trigger model training manually.
    Safe to call multiple times — each call overwrites the previous model.
    Useful after loading new data into the warehouse.
    """
    try:
        result = train_salary_model(db)
        return {"success": True, **result}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"[ML] /train/salary error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error during training.")


# =============================================================================
# GET /api/v1/ml/anomalies
# =============================================================================

@router.get(
    "/anomalies",
    response_model=AnomalyDetectionResponse,
    summary="Z-score anomaly detection for salary and skill demand",
    description=(
        "Detects statistically unusual salary values (per role) and skill demand "
        "values (per skill) for the specified year using z-score analysis. "
        "Default threshold: |z| > 2.0 (flags top/bottom ~5% of deviations). "
        "Returns salary_anomalies and skill_anomalies separately."
    ),
)
def anomaly_detection(
    year: int = Query(default=2024, ge=2018, le=2024),
    z_threshold: float = Query(default=2.0, ge=1.0, le=4.0,
                               description="Z-score threshold. Higher = stricter (fewer alerts)."),
    db: Session = Depends(get_db),
) -> AnomalyDetectionResponse:
    """
    Example response:
        {
            "salary_anomalies": [
                {
                    "role_name": "Chief Data Officer",
                    "year": 2024,
                    "avg_salary_usd": 217455.65,
                    "expected_salary": 145000.00,
                    "z_score": 2.41,
                    "deviation_pct": 49.97,
                    "anomaly_type": "spike"
                }
            ],
            "skill_anomalies": [...],
            "z_score_threshold": 2.0,
            "total_anomalies": 5,
            "year_analyzed": 2024
        }
    """
    try:
        salary_anomalies = detect_salary_anomalies(db, year=year, z_threshold=z_threshold)
        skill_anomalies  = detect_skill_anomalies(db, year=year, z_threshold=z_threshold)

        return AnomalyDetectionResponse(
            salary_anomalies  = [SalaryAnomaly(**a) for a in salary_anomalies],
            skill_anomalies   = [SkillAnomaly(**a) for a in skill_anomalies],
            z_score_threshold = z_threshold,
            total_anomalies   = len(salary_anomalies) + len(skill_anomalies),
            year_analyzed     = year,
        )
    except Exception as e:
        logger.exception(f"[ML] /anomalies error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in anomaly detection.")