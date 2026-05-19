"""
api/models/__init__.py
======================
Exports all ORM models from a single import point.

Usage anywhere in the project:
    from api.models import DimCountry, FactJobPostings

Import order matters:
  Dimensions must be imported before Facts because Facts define
  ForeignKey references to dimension tables. SQLAlchemy resolves
  these by table name string, but Python needs the classes registered
  in Base.metadata first.
"""

from api.models.dimensions import DimCountry, DimIndustry, DimJobRole, DimSkill
from api.models.facts import (
    FactAiDisruption,
    FactJobPostings,
    FactSalaryTrends,
    FactSkillDemand,
)

__all__ = [
    # Dimensions
    "DimCountry",
    "DimIndustry",
    "DimJobRole",
    "DimSkill",
    # Facts
    "FactJobPostings",
    "FactSalaryTrends",
    "FactSkillDemand",
    "FactAiDisruption",
]