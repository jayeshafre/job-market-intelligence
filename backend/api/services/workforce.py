"""
api/services/workforce.py
=========================
Database query functions for Workforce Analytics.

All functions:
  • Accept a SQLAlchemy Session (injected by FastAPI's get_db dependency)
  • Return list[dict] — plain Python dicts that Pydantic schemas can consume
  • Use SQLAlchemy 2.0 select() style for modern, type-safe queries

Tables used: fact_job_postings, dim_country, dim_industry, dim_job_role
"""

from sqlalchemy import select, func, extract, desc, case, cast, Integer
from sqlalchemy.orm import Session

from api.models import DimCountry, DimIndustry, DimJobRole, FactJobPostings


# ─── Helper ───────────────────────────────────────────────────────────────────

def _rows_to_dicts(rows) -> list[dict]:
    """Convert SQLAlchemy Row objects → plain dicts."""
    return [dict(row._mapping) for row in rows]


# =============================================================================
# 1. Hiring Trends — yearly aggregate
# =============================================================================

def get_hiring_trends(
    db: Session,
    start_year: int = 2018,
    end_year: int = 2024,
) -> list[dict]:
    """
    Returns total job postings and avg salary for each year in range.
    Powers the main "Hiring Trend Over Time" line chart on the dashboard.

    SQL logic:
      GROUP BY year, SUM(posting_count), AVG(salary_usd_avg),
      SUM(posting_count WHERE is_remote = true)
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    stmt = (
        select(
            year_col.label("year"),
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.round(func.avg(FactJobPostings.salary_usd_avg), 2).label("avg_salary_usd"),
            func.sum(
                case(
                    (FactJobPostings.is_remote == True, FactJobPostings.posting_count),
                    else_=0,
                )
            ).label("remote_postings"),
        )
        .where(year_col.between(start_year, end_year))
        .group_by(year_col)
        .order_by(year_col)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 2. Hiring by Country
# =============================================================================

def get_hiring_by_country(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    Returns top N countries by total job postings for a given year.
    Powers the choropleth map / country bar chart on the dashboard.
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    stmt = (
        select(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.round(func.avg(FactJobPostings.salary_usd_avg), 2).label("avg_salary_usd"),
        )
        .join(DimCountry, FactJobPostings.country_id == DimCountry.country_id)
        .where(year_col == year)
        .group_by(
            DimCountry.country_name,
            DimCountry.country_code,
            DimCountry.region,
        )
        .order_by(desc("total_postings"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 3. Hiring by Industry
# =============================================================================

def get_hiring_by_industry(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    Returns top N industries by total job postings for a given year.
    Powers the industry breakdown bar/pie chart on the dashboard.
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    stmt = (
        select(
            DimIndustry.industry_name,
            DimIndustry.sector,
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.round(func.avg(FactJobPostings.salary_usd_avg), 2).label("avg_salary_usd"),
            DimIndustry.ai_adoption_index,
        )
        .join(DimIndustry, FactJobPostings.industry_id == DimIndustry.industry_id)
        .where(year_col == year)
        .group_by(
            DimIndustry.industry_name,
            DimIndustry.sector,
            DimIndustry.ai_adoption_index,
        )
        .order_by(desc("total_postings"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 4. Remote Work Breakdown
# =============================================================================

def get_remote_stats(
    db: Session,
    year: int = 2024,
) -> dict:
    """
    Returns remote vs on-site posting split for a given year.
    Powers the remote work donut chart on the dashboard.
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    stmt = (
        select(
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.sum(
                case(
                    (FactJobPostings.is_remote == True, FactJobPostings.posting_count),
                    else_=0,
                )
            ).label("remote_postings"),
        )
        .where(year_col == year)
    )
    row = db.execute(stmt).one()
    total = int(row.total_postings or 0)
    remote = int(row.remote_postings or 0)
    onsite = total - remote
    remote_pct = round((remote / total * 100), 2) if total > 0 else 0.0

    return {
        "total_postings": total,
        "remote_postings": remote,
        "onsite_postings": onsite,
        "remote_pct": remote_pct,
    }


# =============================================================================
# 5. Top Job Roles by Posting Volume
# =============================================================================

def get_top_roles(
    db: Session,
    year: int = 2024,
    limit: int = 10,
) -> list[dict]:
    """
    Returns top N job roles by posting count for a given year.
    Powers the "Most In-Demand Roles" leaderboard.
    """
    year_col = cast(extract("year", FactJobPostings.posting_date), Integer)

    stmt = (
        select(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
            DimJobRole.is_remote_eligible,
            func.sum(FactJobPostings.posting_count).label("total_postings"),
            func.round(func.avg(FactJobPostings.salary_usd_avg), 2).label("avg_salary_usd"),
        )
        .join(DimJobRole, FactJobPostings.role_id == DimJobRole.role_id)
        .where(year_col == year)
        .group_by(
            DimJobRole.role_name,
            DimJobRole.role_category,
            DimJobRole.seniority_level,
            DimJobRole.is_remote_eligible,
        )
        .order_by(desc("total_postings"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())