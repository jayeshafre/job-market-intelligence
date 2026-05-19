"""
api/models/facts.py
===================
SQLAlchemy ORM models for the 4 fact tables.

Fact tables = the measured events/metrics (the "how much / how many" data).
They are large and reference dimension tables via foreign keys.

Tables defined here:
  • FactJobPostings    → fact_job_postings    (34,020 rows)
  • FactSalaryTrends   → fact_salary_trends   (34,020 rows)
  • FactSkillDemand    → fact_skill_demand    (504,000 rows)
  • FactAiDisruption   → fact_ai_disruption   (11,340 rows)

CRITICAL: All CANONICAL KPI field names match warehouse_schema.sql exactly:
  salary_growth_pct, growth_pct, automation_risk_score,
  ai_replacement_index, future_safe_score, demand_score, salary_usd_avg
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, ForeignKey,
    Integer, Numeric, SmallInteger, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


# =============================================================================
# FactJobPostings
# =============================================================================

class FactJobPostings(Base):
    """
    Maps to: fact_job_postings
    Purpose: 34,020 job posting events with salary and context (2018–2024).
    Grain: one row = one job posting event (or aggregated similar postings).
    """
    __tablename__ = "fact_job_postings"

    __table_args__ = (
        CheckConstraint("salary_usd_min >= 0",           name="ck_posting_salary_min"),
        CheckConstraint("salary_usd_max >= 0",           name="ck_posting_salary_max"),
        CheckConstraint("salary_usd_avg >= 0",           name="ck_posting_salary_avg"),
        CheckConstraint(
            "experience_years_req BETWEEN 0 AND 50",
            name="ck_posting_experience_range"
        ),
        CheckConstraint("posting_count > 0",             name="ck_posting_count_positive"),
    )

    # Primary Key
    posting_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_job_role.role_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_country.country_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    industry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_industry.industry_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Event Data
    posting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    salary_usd_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_usd_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_usd_avg: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True,
        comment="CANONICAL KPI — Computed average salary in USD"
    )
    is_remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    experience_years_req: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    posting_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Aggregated similar postings"
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    job_role: Mapped["DimJobRole"] = relationship(
        "DimJobRole", back_populates="job_postings", lazy="joined"
    )
    country: Mapped["DimCountry"] = relationship(
        "DimCountry", back_populates="job_postings", lazy="joined"
    )
    industry: Mapped["DimIndustry"] = relationship(
        "DimIndustry", back_populates="job_postings", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<FactJobPostings id={self.posting_id} date={self.posting_date} "
            f"role={self.role_id} salary_avg={self.salary_usd_avg}>"
        )


# =============================================================================
# FactSalaryTrends
# =============================================================================

class FactSalaryTrends(Base):
    """
    Maps to: fact_salary_trends
    Purpose: Annual salary trends per role × country (2018–2024).
    Grain: one row = one role × country × year (× quarter if quarterly).
    Note: quarter is NULL for annual aggregates (no quarterly data in synthetic set).
    """
    __tablename__ = "fact_salary_trends"

    __table_args__ = (
        CheckConstraint("year BETWEEN 2000 AND 2100",    name="ck_salary_year_range"),
        CheckConstraint("quarter BETWEEN 1 AND 4",       name="ck_salary_quarter_range"),
        CheckConstraint("avg_salary_usd >= 0",           name="ck_salary_avg_usd"),
        CheckConstraint("median_salary_usd >= 0",        name="ck_salary_median_usd"),
        UniqueConstraint(
            "role_id", "country_id", "year", "quarter",
            name="uq_salary_trends"
        ),
    )

    # Primary Key
    trend_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_job_role.role_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_country.country_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Time Dimension
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    quarter: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True,
        comment="NULL = annual figure; 1–4 = quarterly"
    )

    # KPI Fields
    avg_salary_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    salary_growth_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True,
        comment="CANONICAL KPI — YoY salary growth %; NULL for first year (no baseline)"
    )
    median_salary_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    job_role: Mapped["DimJobRole"] = relationship(
        "DimJobRole", back_populates="salary_trends", lazy="joined"
    )
    country: Mapped["DimCountry"] = relationship(
        "DimCountry", back_populates="salary_trends", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<FactSalaryTrends id={self.trend_id} role={self.role_id} "
            f"country={self.country_id} year={self.year} avg={self.avg_salary_usd}>"
        )


# =============================================================================
# FactSkillDemand
# =============================================================================

class FactSkillDemand(Base):
    """
    Maps to: fact_skill_demand
    Purpose: Skill demand by skill × industry × country × year.
    Grain: one row = one skill × industry × country × year.
    Note: Largest table (504,000 rows) — composite index on (skill_id, industry_id, year)
          is critical for query performance. Already defined in warehouse_schema.sql.
    """
    __tablename__ = "fact_skill_demand"

    __table_args__ = (
        CheckConstraint("year BETWEEN 2000 AND 2100",       name="ck_demand_year_range"),
        CheckConstraint("demand_score BETWEEN 0 AND 100",   name="ck_demand_score_range"),
        CheckConstraint("mention_count >= 0",               name="ck_demand_mention_count"),
        UniqueConstraint(
            "skill_id", "industry_id", "country_id", "year",
            name="uq_skill_demand"
        ),
    )

    # Primary Key
    demand_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Foreign Keys
    skill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_skill.skill_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    industry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_industry.industry_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_country.country_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Time Dimension
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)

    # KPI Fields
    demand_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="CANONICAL KPI — Demand index 0–100 based on job listing mention frequency"
    )
    mention_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Raw job listing mentions"
    )
    growth_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True,
        comment="CANONICAL KPI — YoY demand growth %; NULL for first year"
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    skill: Mapped["DimSkill"] = relationship(
        "DimSkill", back_populates="skill_demands", lazy="joined"
    )
    industry: Mapped["DimIndustry"] = relationship(
        "DimIndustry", back_populates="skill_demands", lazy="joined"
    )
    country: Mapped["DimCountry"] = relationship(
        "DimCountry", back_populates="skill_demands", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<FactSkillDemand id={self.demand_id} skill={self.skill_id} "
            f"year={self.year} demand={self.demand_score} growth={self.growth_pct}>"
        )


# =============================================================================
# FactAiDisruption
# =============================================================================

class FactAiDisruption(Base):
    """
    Maps to: fact_ai_disruption
    Purpose: AI disruption scores per role × industry × year.
    Grain: one row = one role × industry × year.
    Note: future_safe_score = 100 - automation_risk_score (derived KPI).
    """
    __tablename__ = "fact_ai_disruption"

    __table_args__ = (
        CheckConstraint("year BETWEEN 2000 AND 2100",               name="ck_disruption_year_range"),
        CheckConstraint("automation_risk_score BETWEEN 0 AND 100",  name="ck_disruption_risk_range"),
        CheckConstraint("ai_replacement_index BETWEEN 0 AND 100",   name="ck_disruption_replacement_range"),
        CheckConstraint("future_safe_score BETWEEN 0 AND 100",      name="ck_disruption_safe_range"),
        UniqueConstraint(
            "role_id", "industry_id", "year",
            name="uq_ai_disruption"
        ),
    )

    # Primary Key
    disruption_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_job_role.role_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    industry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_industry.industry_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Time Dimension
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)

    # KPI Fields — ALL CANONICAL, names locked to warehouse_schema.sql
    automation_risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="CANONICAL KPI — 0–100 probability of automation within 10 years"
    )
    ai_replacement_index: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="CANONICAL KPI — 0–100 composite AI replacement likelihood score"
    )
    future_safe_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="CANONICAL KPI — Derived: 100 - automation_risk_score"
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    job_role: Mapped["DimJobRole"] = relationship(
        "DimJobRole", back_populates="ai_disruptions", lazy="joined"
    )
    industry: Mapped["DimIndustry"] = relationship(
        "DimIndustry", back_populates="ai_disruptions", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<FactAiDisruption id={self.disruption_id} role={self.role_id} "
            f"industry={self.industry_id} year={self.year} "
            f"risk={self.automation_risk_score} safe={self.future_safe_score}>"
        )


# ── Forward reference imports ─────────────────────────────────────────────────
from api.models.dimensions import DimCountry, DimIndustry, DimJobRole, DimSkill  # noqa: E402, F401