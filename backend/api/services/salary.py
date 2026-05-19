"""
api/services/salary.py
======================
Database query functions for Salary Intelligence.

Uses fact_salary_trends (pre-aggregated per role×country×year) for all
salary analysis — it's purpose-built for this and far faster than
aggregating raw fact_job_postings every time.

Tables used: fact_salary_trends, dim_job_role, dim_country
"""

from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from api.models import DimCountry, DimJobRole, FactSalaryTrends


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


# =============================================================================
# 1. Salary by Role
# =============================================================================

def get_salary_by_role(
    db: Session,
    year: int = 2024,
    seniority_level: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """
    Average salary per job role, optionally filtered by seniority.
    Powers the "Salary by Role" bar chart.
    """
    stmt = (
        select(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
            func.count(FactSalaryTrends.trend_id).label("data_points"),
        )
        .join(DimJobRole, FactSalaryTrends.role_id == DimJobRole.role_id)
        .where(FactSalaryTrends.year == year)
        .group_by(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
        )
        .order_by(desc("avg_salary_usd"))
        .limit(limit)
    )

    # Apply optional seniority filter
    if seniority_level:
        stmt = stmt.where(DimJobRole.seniority_level == seniority_level)

    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 2. Salary by Country
# =============================================================================

def get_salary_by_country(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    Average salary per country for a given year.
    Powers the "Country Salary Comparison" chart.
    """
    stmt = (
        select(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
            func.count(FactSalaryTrends.trend_id).label("data_points"),
        )
        .join(DimCountry, FactSalaryTrends.country_id == DimCountry.country_id)
        .where(FactSalaryTrends.year == year)
        .group_by(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
        )
        .order_by(desc("avg_salary_usd"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 3. Salary Trend Over Time
# =============================================================================

def get_salary_trends(
    db: Session,
    start_year: int = 2018,
    end_year: int = 2024,
    role_id: int | None = None,
    country_id: int | None = None,
) -> list[dict]:
    """
    Year-over-year salary trend with growth %.
    Optional filters: specific role or country for drill-down.
    Powers the "Salary Growth Over Time" line chart.

    salary_growth_pct: NULLs for the earliest year (no baseline to compare against).
    """
    stmt = (
        select(
            FactSalaryTrends.year,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
            func.round(func.avg(FactSalaryTrends.salary_growth_pct), 2).label("salary_growth_pct"),
            func.round(func.avg(FactSalaryTrends.median_salary_usd), 2).label("median_salary_usd"),
        )
        .where(
            FactSalaryTrends.year.between(start_year, end_year),
            FactSalaryTrends.quarter.is_(None),  # annual figures only
        )
        .group_by(FactSalaryTrends.year)
        .order_by(FactSalaryTrends.year)
    )

    if role_id is not None:
        stmt = stmt.where(FactSalaryTrends.role_id == role_id)
    if country_id is not None:
        stmt = stmt.where(FactSalaryTrends.country_id == country_id)

    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 4. Top Paying Roles
# =============================================================================

def get_top_paying_roles(
    db: Session,
    year: int = 2024,
    limit: int = 10,
) -> list[dict]:
    """
    Top N highest-paying job roles. Adds a rank number for the frontend.
    Powers the "Top Paying Roles" leaderboard widget.
    """
    stmt = (
        select(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
        )
        .join(DimJobRole, FactSalaryTrends.role_id == DimJobRole.role_id)
        .where(FactSalaryTrends.year == year)
        .group_by(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
        )
        .order_by(desc("avg_salary_usd"))
        .limit(limit)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())

    # Add rank numbers (1-based) — done in Python to avoid window function complexity
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


# =============================================================================
# 5. Top Paying Countries
# =============================================================================

def get_top_paying_countries(
    db: Session,
    year: int = 2024,
    limit: int = 10,
) -> list[dict]:
    """
    Top N highest-paying countries by average salary.
    Powers the "Best Countries for Salary" leaderboard.
    """
    stmt = (
        select(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
            func.round(func.avg(FactSalaryTrends.avg_salary_usd), 2).label("avg_salary_usd"),
        )
        .join(DimCountry, FactSalaryTrends.country_id == DimCountry.country_id)
        .where(FactSalaryTrends.year == year)
        .group_by(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
        )
        .order_by(desc("avg_salary_usd"))
        .limit(limit)
    )
    rows = _rows_to_dicts(db.execute(stmt).all())
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows