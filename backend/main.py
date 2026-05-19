"""
main.py
=======
FastAPI application entry point — Phase 3 complete.

Run:
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

All endpoints:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.database import test_connection
from api.schemas import ErrorResponse, HealthResponse
from api.routers import workforce, salary, skills, ai_impact
from api.routers import analytics, forecast
from api.routers import ai

settings = get_settings()


# =============================================================================
# LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 60)
    print(f"  {settings.APP_TITLE}")
    print(f"  Version  : {settings.APP_VERSION}")
    print(f"  Env      : {settings.APP_ENV}")
    print("=" * 60)

    db_status = test_connection()
    if db_status["status"] == "connected":
        print(f"  DB       : {db_status['database']}@{db_status['host']} ✓")
        print(f"  PG       : {db_status.get('pg_version', '')[:40]}")
    else:
        print(f"  DB       : CONNECTION FAILED ✗")
        print(f"  Error    : {db_status.get('error', 'unknown')}")

    print("=" * 60 + "\n")
    app.state.db_status = db_status
    app.state.startup_time = datetime.now(timezone.utc)

    yield

    print("\n[shutdown] Job Market API shutting down cleanly.")


# =============================================================================
# APP
# =============================================================================

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# =============================================================================
# MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found",
            detail=f"The endpoint {request.url.path} does not exist.",
        ).model_dump(mode="json"),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Check server logs.",
        ).model_dump(mode="json"),
    )

# =============================================================================
# SYSTEM ROUTES
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    db_info = getattr(app.state, "db_status", {"status": "unknown"})
    return HealthResponse(
        status="ok" if db_info.get("status") == "connected" else "degraded",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
        database=db_info,
    )


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "message": f"Welcome to {settings.APP_TITLE}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }

# =============================================================================
# ANALYTICS ROUTERS — Phase 2
# =============================================================================

app.include_router(workforce.router, prefix="/api/v1/workforce",  tags=["Workforce Analytics"])
app.include_router(salary.router,    prefix="/api/v1/salary",     tags=["Salary Intelligence"])
app.include_router(skills.router,    prefix="/api/v1/skills",     tags=["Skill Intelligence"])
app.include_router(ai_impact.router, prefix="/api/v1/ai-impact",  tags=["AI Impact Analytics"])

# =============================================================================
# ANALYTICS ENGINE + FORECASTING — Phase 3
# =============================================================================

app.include_router(analytics.router, prefix="/api/v1/analytics",  tags=["Analytics Engine"])
app.include_router(forecast.router,  prefix="/api/v1/forecast",   tags=["Forecasting Engine"])

# =============================================================================
# AI ASSISTANT — Phase 1
# =============================================================================
 
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Assistant"])