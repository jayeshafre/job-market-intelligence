"""
api/services/skills.py
======================
Database query functions for Skill Intelligence.

fact_skill_demand has 504,000 rows — always filter by year and use LIMIT
to keep queries fast. The composite index on (skill_id, industry_id, year)
defined in warehouse_schema.sql makes these queries performant.

Tables used: fact_skill_demand, dim_skill, dim_industry, dim_country
"""

from sqlalchemy import select, func, desc, cast, Integer
from sqlalchemy.orm import Session

from api.models import DimSkill, DimIndustry, FactSkillDemand


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


# =============================================================================
# 1. Top Growing Skills
# =============================================================================

def get_top_growing_skills(
    db: Session,
    year: int = 2024,
    limit: int = 15,
    ai_only: bool = False,
) -> list[dict]:
    """
    Top N skills ranked by average YoY demand growth %.
    Optional filter: ai_only=True → only AI/ML skills.
    Powers the "Fastest Growing Skills" bar chart.
    """
    stmt = (
        select(
            DimSkill.skill_name,
            DimSkill.skill_category,
            DimSkill.is_ai_related,
            # Use dim_skill.growth_pct as the primary growth signal
            # (pre-computed YoY from the data generation layer)
            DimSkill.growth_pct,
            func.round(func.avg(FactSkillDemand.demand_score), 2).label("avg_demand_score"),
        )
        .join(DimSkill, FactSkillDemand.skill_id == DimSkill.skill_id)
        .where(FactSkillDemand.year == year)
        .group_by(
            DimSkill.skill_name,
            DimSkill.skill_category,
            DimSkill.is_ai_related,
            DimSkill.growth_pct,
        )
        .order_by(desc(DimSkill.growth_pct))
        .limit(limit)
    )

    if ai_only:
        stmt = stmt.where(DimSkill.is_ai_related == True)  # noqa: E712

    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 2. AI/ML Skills Demand
# =============================================================================

def get_ai_skills(
    db: Session,
    year: int = 2024,
    limit: int = 20,
) -> list[dict]:
    """
    All AI-related skills with their demand score and mention count.
    Powers the "AI Skill Demand" section of the dashboard.
    """
    stmt = (
        select(
            DimSkill.skill_name,
            DimSkill.skill_category,
            func.round(func.avg(FactSkillDemand.demand_score), 2).label("avg_demand_score"),
            func.round(func.avg(FactSkillDemand.growth_pct), 2).label("avg_growth_pct"),
            func.sum(FactSkillDemand.mention_count).label("total_mentions"),
        )
        .join(DimSkill, FactSkillDemand.skill_id == DimSkill.skill_id)
        .where(
            FactSkillDemand.year == year,
            DimSkill.is_ai_related == True,  # noqa: E712
        )
        .group_by(
            DimSkill.skill_name,
            DimSkill.skill_category,
        )
        .order_by(desc("avg_demand_score"))
        .limit(limit)
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 3. Skills by Category
# =============================================================================

def get_skills_by_category(
    db: Session,
    year: int = 2024,
) -> list[dict]:
    """
    Skill demand grouped and summarised by category.
    Answers: "Which category of skills is growing fastest?"
    Powers the category comparison chart.
    """
    stmt = (
        select(
            DimSkill.skill_category,
            func.count(func.distinct(DimSkill.skill_id)).label("skill_count"),
            func.round(func.avg(DimSkill.growth_pct), 2).label("avg_growth_pct"),
            func.sum(
                cast(DimSkill.is_ai_related, Integer)
            ).label("ai_skill_count"),
        )
        .join(FactSkillDemand, FactSkillDemand.skill_id == DimSkill.skill_id)
        .where(FactSkillDemand.year == year)
        .group_by(DimSkill.skill_category)
        .order_by(desc("avg_growth_pct"))
    )
    return _rows_to_dicts(db.execute(stmt).all())


# =============================================================================
# 4. Skill Demand Trend (Year Over Year)
# =============================================================================

def get_skill_demand_trends(
    db: Session,
    skill_name: str,
    start_year: int = 2018,
    end_year: int = 2024,
) -> list[dict]:
    """
    Year-over-year demand trend for one specific skill.
    Used for drill-down when a user clicks a skill in the dashboard.
    Powers the skill detail trend line chart.
    """
    stmt = (
        select(
            FactSkillDemand.year,
            DimSkill.skill_name,
            func.round(func.avg(FactSkillDemand.demand_score), 2).label("avg_demand_score"),
            func.round(func.avg(FactSkillDemand.growth_pct), 2).label("avg_growth_pct"),
        )
        .join(DimSkill, FactSkillDemand.skill_id == DimSkill.skill_id)
        .where(
            DimSkill.skill_name.ilike(f"%{skill_name}%"),  # case-insensitive match
            FactSkillDemand.year.between(start_year, end_year),
        )
        .group_by(FactSkillDemand.year, DimSkill.skill_name)
        .order_by(FactSkillDemand.year)
    )
    return _rows_to_dicts(db.execute(stmt).all())