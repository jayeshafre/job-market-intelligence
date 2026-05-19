"""
api/schemas/skills.py
=====================
Pydantic response schemas for the Skill Intelligence router.
"""

from pydantic import BaseModel


class GrowingSkill(BaseModel):
    """A skill ranked by its YoY demand growth."""
    skill_name: str
    skill_category: str
    is_ai_related: bool
    growth_pct: float | None        # CANONICAL KPI
    avg_demand_score: float | None  # CANONICAL KPI


class AISkill(BaseModel):
    """An AI/ML-related skill with its demand metrics."""
    skill_name: str
    skill_category: str
    avg_demand_score: float | None
    avg_growth_pct: float | None
    total_mentions: int | None


class SkillCategorySummary(BaseModel):
    """Skill demand aggregated by category (Programming, Cloud, etc.)."""
    skill_category: str
    skill_count: int
    avg_growth_pct: float | None
    ai_skill_count: int


class SkillDemandTrend(BaseModel):
    """One point on a skill's demand trend chart (year over year)."""
    year: int
    skill_name: str
    avg_demand_score: float | None
    avg_growth_pct: float | None