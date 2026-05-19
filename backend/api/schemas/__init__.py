"""
api/schemas/__init__.py
=======================
Central export for all Pydantic schemas.

Phase 1: HealthResponse, APIResponse, ErrorResponse (system schemas)
Phase 2: Domain schemas — workforce, salary, skills, ai_impact
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# =============================================================================
# System Schemas (Phase 1)
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
    database: dict[str, Any]


class APIResponse(BaseModel, Generic[T]):
    """
    Standard response envelope used by every analytics endpoint.

    {
        "success": true,
        "data": [...],
        "message": "ok",
        "count": 10
    }
    """
    success: bool = True
    data: T
    message: str = "ok"
    count: int | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Domain Schema re-exports (Phase 2)
# =============================================================================

from api.schemas.workforce import (  # noqa: E402
    HiringTrendPoint,
    CountryHiringStats,
    IndustryHiringStats,
    RemoteBreakdown,
    TopRole,
)
from api.schemas.salary import (  # noqa: E402
    RoleSalary,
    CountrySalary,
    SalaryTrendPoint,
    TopPayingRole,
    TopPayingCountry,
)
from api.schemas.skills import (  # noqa: E402
    GrowingSkill,
    AISkill,
    SkillCategorySummary,
    SkillDemandTrend,
)
from api.schemas.ai_impact import (  # noqa: E402
    DisruptionScore,
    FutureSafeCareer,
    IndustryDisruption,
    DisruptionTrend,
)

__all__ = [
    # System
    "HealthResponse", "APIResponse", "ErrorResponse",
    # Workforce
    "HiringTrendPoint", "CountryHiringStats", "IndustryHiringStats",
    "RemoteBreakdown", "TopRole",
    # Salary
    "RoleSalary", "CountrySalary", "SalaryTrendPoint",
    "TopPayingRole", "TopPayingCountry",
    # Skills
    "GrowingSkill", "AISkill", "SkillCategorySummary", "SkillDemandTrend",
    # AI Impact
    "DisruptionScore", "FutureSafeCareer", "IndustryDisruption", "DisruptionTrend",
]