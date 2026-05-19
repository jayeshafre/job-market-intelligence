"""
api/schemas/salary.py
=====================
Pydantic response schemas for the Salary Intelligence router.
"""

from pydantic import BaseModel


class RoleSalary(BaseModel):
    """Average salary figures for a specific job role."""
    role_name: str
    role_category: str
    seniority_level: str
    avg_salary_usd: float
    data_points: int            # number of role×country×year records


class CountrySalary(BaseModel):
    """Average salary figures for a specific country."""
    country_name: str
    country_code: str
    region: str
    avg_salary_usd: float
    data_points: int


class SalaryTrendPoint(BaseModel):
    """One point on a salary-over-time trend chart."""
    year: int
    avg_salary_usd: float
    salary_growth_pct: float | None   # NULL for the first year (no baseline)
    median_salary_usd: float | None


class TopPayingRole(BaseModel):
    """A role in the top-N highest-paying list."""
    rank: int
    role_name: str
    role_category: str
    seniority_level: str
    avg_salary_usd: float


class TopPayingCountry(BaseModel):
    """A country in the top-N highest-paying list."""
    rank: int
    country_name: str
    country_code: str
    region: str
    avg_salary_usd: float