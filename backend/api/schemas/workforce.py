"""
api/schemas/workforce.py
========================
Pydantic response schemas for the Workforce Analytics router.
These define exactly what the API sends to the frontend — nothing more.
"""

from pydantic import BaseModel


class HiringTrendPoint(BaseModel):
    """One data point on the yearly hiring trend chart."""
    year: int
    total_postings: int
    avg_salary_usd: float | None
    remote_postings: int


class CountryHiringStats(BaseModel):
    """Hiring demand aggregated per country."""
    country_name: str
    country_code: str
    region: str
    total_postings: int
    avg_salary_usd: float | None


class IndustryHiringStats(BaseModel):
    """Hiring demand aggregated per industry."""
    industry_name: str
    sector: str
    total_postings: int
    avg_salary_usd: float | None
    ai_adoption_index: float


class RemoteBreakdown(BaseModel):
    """Remote vs on-site split for a given year."""
    total_postings: int
    remote_postings: int
    onsite_postings: int
    remote_pct: float


class TopRole(BaseModel):
    """A single job role ranked by posting volume."""
    role_name: str
    role_category: str
    seniority_level: str
    total_postings: int
    avg_salary_usd: float | None
    is_remote_eligible: bool