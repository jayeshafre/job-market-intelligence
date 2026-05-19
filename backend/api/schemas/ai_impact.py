"""
api/schemas/ai_impact.py
========================
Pydantic response schemas for the AI Impact Analytics router.
All KPI field names match warehouse_schema.sql CANONICAL names exactly.
"""

from pydantic import BaseModel


class DisruptionScore(BaseModel):
    """AI disruption metrics for a specific job role."""
    role_name: str
    role_category: str
    seniority_level: str
    avg_automation_risk: float | None    # CANONICAL: automation_risk_score
    avg_ai_replacement: float | None     # CANONICAL: ai_replacement_index
    avg_future_safe: float | None        # CANONICAL: future_safe_score


class FutureSafeCareer(BaseModel):
    """A career ranked by how safe it is from AI disruption."""
    rank: int
    role_name: str
    role_category: str
    avg_future_safe_score: float | None  # higher = safer
    ai_disruption_risk: float            # from dim_job_role (role-level baseline)
    is_remote_eligible: bool


class IndustryDisruption(BaseModel):
    """AI disruption aggregated per industry."""
    industry_name: str
    sector: str
    avg_automation_risk: float | None
    avg_future_safe: float | None
    ai_adoption_index: float             # from dim_industry


class DisruptionTrend(BaseModel):
    """One point on the AI disruption trend chart (year over year)."""
    year: int
    avg_automation_risk: float | None
    avg_future_safe: float | None
    avg_ai_replacement: float | None