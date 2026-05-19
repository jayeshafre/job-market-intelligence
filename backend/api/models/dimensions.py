"""
api/models/dimensions.py
========================
SQLAlchemy ORM models for the 4 dimension tables.

CRITICAL: Column names, types, and constraints are kept 100% consistent
with warehouse_schema.sql. Any deviation = data integrity bugs at runtime.

Dimension tables = reference / lookup data (the "who/what/where" context).
They are small, stable, and loaded once.

Tables defined here:
  • DimCountry    → dim_country    (60 rows)
  • DimIndustry   → dim_industry   (20 rows)
  • DimJobRole    → dim_job_role   (81 rows)
  • DimSkill      → dim_skill      (60 rows)
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Integer,
    Numeric, SmallInteger, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


# =============================================================================
# DimCountry
# =============================================================================

class DimCountry(Base):
    """
    Maps to: dim_country
    Purpose: Reference table for 60 countries with regional classification.
    """
    __tablename__ = "dim_country"

    # Primary Key
    country_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Columns — match warehouse_schema.sql exactly
    country_code: Mapped[str] = mapped_column(
        String(3), nullable=False, unique=True,
        comment="ISO 3166-1 alpha-2/3 (e.g. US, IND, GBR)"
    )
    country_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    region: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Americas, Europe, Asia, Africa, Oceania"
    )
    sub_region: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="e.g. South Asia, Western Europe"
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), nullable=False,
        comment="ISO 4217 (e.g. USD, EUR, INR)"
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships (back-populated by fact models) ─────────────────────
    job_postings: Mapped[list["FactJobPostings"]] = relationship(
        "FactJobPostings", back_populates="country", lazy="select"
    )
    salary_trends: Mapped[list["FactSalaryTrends"]] = relationship(
        "FactSalaryTrends", back_populates="country", lazy="select"
    )
    skill_demands: Mapped[list["FactSkillDemand"]] = relationship(
        "FactSkillDemand", back_populates="country", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<DimCountry id={self.country_id} code={self.country_code} name={self.country_name}>"


# =============================================================================
# DimIndustry
# =============================================================================

class DimIndustry(Base):
    """
    Maps to: dim_industry
    Purpose: 20 industries with sector groupings and AI adoption scores.
    """
    __tablename__ = "dim_industry"

    __table_args__ = (
        CheckConstraint(
            "ai_adoption_index BETWEEN 0 AND 100",
            name="ck_industry_ai_adoption_range"
        ),
    )

    # Primary Key
    industry_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Columns
    industry_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    sector: Mapped[str] = mapped_column(
        String(80), nullable=False,
        comment="Technology, Finance, Healthcare, Commerce ..."
    )
    ai_adoption_index: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False,
        comment="0–100; higher = more AI-adopted industry"
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    job_postings: Mapped[list["FactJobPostings"]] = relationship(
        "FactJobPostings", back_populates="industry", lazy="select"
    )
    skill_demands: Mapped[list["FactSkillDemand"]] = relationship(
        "FactSkillDemand", back_populates="industry", lazy="select"
    )
    ai_disruptions: Mapped[list["FactAiDisruption"]] = relationship(
        "FactAiDisruption", back_populates="industry", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<DimIndustry id={self.industry_id} name={self.industry_name} sector={self.sector}>"


# =============================================================================
# DimJobRole
# =============================================================================

class DimJobRole(Base):
    """
    Maps to: dim_job_role
    Purpose: 81 job roles with seniority, remote eligibility, and AI disruption risk.
    """
    __tablename__ = "dim_job_role"

    # Valid seniority values — mirrors the CHECK constraint in the schema
    SENIORITY_LEVELS = ("Entry", "Mid", "Senior", "Director", "C-Suite")

    __table_args__ = (
        CheckConstraint(
            "seniority_level IN ('Entry','Mid','Senior','Director','C-Suite')",
            name="ck_role_seniority_level"
        ),
        CheckConstraint(
            "ai_disruption_risk BETWEEN 0 AND 100",
            name="ck_role_ai_disruption_risk_range"
        ),
    )

    # Primary Key
    role_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Columns
    role_name: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True
    )
    role_category: Mapped[str] = mapped_column(
        String(80), nullable=False,
        comment="Engineering, Analytics, Management, Design ..."
    )
    seniority_level: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="Entry | Mid | Senior | Director | C-Suite"
    )
    is_remote_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    ai_disruption_risk: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False,
        comment="CANONICAL KPI: 0–100 automation risk at role level"
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    job_postings: Mapped[list["FactJobPostings"]] = relationship(
        "FactJobPostings", back_populates="job_role", lazy="select"
    )
    salary_trends: Mapped[list["FactSalaryTrends"]] = relationship(
        "FactSalaryTrends", back_populates="job_role", lazy="select"
    )
    ai_disruptions: Mapped[list["FactAiDisruption"]] = relationship(
        "FactAiDisruption", back_populates="job_role", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<DimJobRole id={self.role_id} name={self.role_name} "
            f"level={self.seniority_level} risk={self.ai_disruption_risk}>"
        )


# =============================================================================
# DimSkill
# =============================================================================

class DimSkill(Base):
    """
    Maps to: dim_skill
    Purpose: 60 skills with category, AI flag, and YoY growth percentage.
    """
    __tablename__ = "dim_skill"

    # Primary Key
    skill_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Columns
    skill_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    skill_category: Mapped[str] = mapped_column(
        String(80), nullable=False,
        comment="Programming, Framework, Cloud, Domain, Soft Skill"
    )
    is_ai_related: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="TRUE if skill belongs to AI/ML ecosystem"
    )
    growth_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True,
        comment="CANONICAL KPI: YoY demand growth %"
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    skill_demands: Mapped[list["FactSkillDemand"]] = relationship(
        "FactSkillDemand", back_populates="skill", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<DimSkill id={self.skill_id} name={self.skill_name} "
            f"ai={self.is_ai_related} growth={self.growth_pct}>"
        )


# ── Forward reference imports (placed at bottom to avoid circular imports) ────
# These are imported AFTER class definitions so Python resolves them correctly.
from api.models.facts import FactJobPostings, FactSalaryTrends, FactSkillDemand, FactAiDisruption  # noqa: E402, F401