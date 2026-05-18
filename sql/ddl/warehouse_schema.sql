-- =============================================================================
-- WORKSPACE 2 — DATA & ANALYTICS
-- AI-Powered Global Job Market Intelligence & Workforce Analytics Platform
-- FILE: warehouse_schema.sql
-- PURPOSE: PostgreSQL Star Schema — Dimension & Fact Tables
-- VERSION: 1.0
-- CREATED: 2025–2026 MCA Final Year Project
-- =============================================================================
-- NOTES:
--   • All monetary values stored in USD
--   • All percentage KPIs use NUMERIC(6,2) to support values like -100.00 to +999.99
--   • KPI field names here are CANONICAL — must remain consistent across all workspaces:
--       salary_growth_pct, growth_pct, automation_risk_score,
--       ai_replacement_index, future_safe_score, demand_score
--   • Schema follows star schema pattern: fact tables reference dimension tables via FK
--   • Run this file in order: extensions → dimensions → facts → indexes → comments
-- =============================================================================


-- =============================================================================
-- 0. EXTENSIONS
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- for UUID generation if needed later


-- =============================================================================
-- 1. DIMENSION TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1.1 dim_country
--     Reference table for 60 countries with regional classification.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_country (
    country_id      SERIAL          PRIMARY KEY,
    country_code    VARCHAR(3)      NOT NULL UNIQUE,                        -- ISO 3166-1 alpha-2/3 (e.g. US, IND, GBR)
    country_name    VARCHAR(100)    NOT NULL,
    region          VARCHAR(50)     NOT NULL,                               -- Americas, Europe, Asia, Africa, Oceania
    sub_region      VARCHAR(50),                                            -- e.g. South Asia, Western Europe
    currency_code   VARCHAR(3)      NOT NULL,                               -- ISO 4217 (e.g. USD, EUR, INR)

    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 1.2 dim_industry
--     20 industries with their sector groupings and AI adoption scores.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_industry (
    industry_id         SERIAL          PRIMARY KEY,
    industry_name       VARCHAR(100)    NOT NULL UNIQUE,
    sector              VARCHAR(80)     NOT NULL,                           -- Technology, Finance, Healthcare, Commerce ...
    ai_adoption_index   NUMERIC(5,2)    NOT NULL                           -- 0–100; higher = more AI-adopted industry
                            CHECK (ai_adoption_index BETWEEN 0 AND 100),

    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 1.3 dim_job_role
--     81 job roles with seniority, remote eligibility, and disruption risk.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_job_role (
    role_id             SERIAL          PRIMARY KEY,
    role_name           VARCHAR(150)    NOT NULL UNIQUE,
    role_category       VARCHAR(80)     NOT NULL,                          -- Engineering, Analytics, Management, Design ...
    seniority_level     VARCHAR(30)     NOT NULL                           -- Entry, Mid, Senior, Director, C-Suite
                            CHECK (seniority_level IN ('Entry','Mid','Senior','Director','C-Suite')),
    is_remote_eligible  BOOLEAN         NOT NULL DEFAULT FALSE,
    ai_disruption_risk  NUMERIC(5,2)    NOT NULL                           -- CANONICAL KPI: 0–100
                            CHECK (ai_disruption_risk BETWEEN 0 AND 100),

    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 1.4 dim_skill
--     60 skills with category, AI flag, and YoY growth percentage.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_skill (
    skill_id        SERIAL          PRIMARY KEY,
    skill_name      VARCHAR(100)    NOT NULL UNIQUE,
    skill_category  VARCHAR(80)     NOT NULL,                              -- Programming, Framework, Cloud, Domain, Soft Skill
    is_ai_related   BOOLEAN         NOT NULL DEFAULT FALSE,                -- TRUE if skill belongs to AI/ML ecosystem
    growth_pct      NUMERIC(6,2),                                          -- CANONICAL KPI: YoY demand growth %

    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- =============================================================================
-- 2. FACT TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 fact_job_postings
--     34,020 rows. Each row = one job posting event with salary and context.
--     Date range: 2018-01-01 to 2024-12-28.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_job_postings (
    posting_id              SERIAL          PRIMARY KEY,

    -- Foreign Keys
    role_id                 INT             NOT NULL REFERENCES dim_job_role(role_id)  ON DELETE RESTRICT,
    country_id              INT             NOT NULL REFERENCES dim_country(country_id) ON DELETE RESTRICT,
    industry_id             INT             NOT NULL REFERENCES dim_industry(industry_id) ON DELETE RESTRICT,

    -- Event Data
    posting_date            DATE            NOT NULL,
    salary_usd_min          NUMERIC(12,2)   CHECK (salary_usd_min >= 0),
    salary_usd_max          NUMERIC(12,2)   CHECK (salary_usd_max >= 0),
    salary_usd_avg          NUMERIC(12,2)   CHECK (salary_usd_avg >= 0),  -- CANONICAL KPI field
    is_remote               BOOLEAN         NOT NULL DEFAULT FALSE,
    experience_years_req    SMALLINT        NOT NULL DEFAULT 0             -- 0 to 21 years per data
                                CHECK (experience_years_req BETWEEN 0 AND 50),
    posting_count           INT             NOT NULL DEFAULT 1             -- aggregated similar postings
                                CHECK (posting_count > 0),

    created_at              TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 2.2 fact_salary_trends
--     34,020 rows. Annual salary trends per role and country (2018–2024).
--     quarter column is NULL for annual aggregates (no quarterly splits in data).
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_salary_trends (
    trend_id            SERIAL          PRIMARY KEY,

    -- Foreign Keys
    role_id             INT             NOT NULL REFERENCES dim_job_role(role_id)  ON DELETE RESTRICT,
    country_id          INT             NOT NULL REFERENCES dim_country(country_id) ON DELETE RESTRICT,

    -- Time Dimension
    year                SMALLINT        NOT NULL CHECK (year BETWEEN 2000 AND 2100),
    quarter             SMALLINT                 CHECK (quarter BETWEEN 1 AND 4),    -- NULL = annual figure

    -- KPI Fields
    avg_salary_usd      NUMERIC(12,2)   NOT NULL CHECK (avg_salary_usd >= 0),
    salary_growth_pct   NUMERIC(6,2),                                                -- CANONICAL KPI; NULL for first year (no prior baseline)
    median_salary_usd   NUMERIC(12,2)            CHECK (median_salary_usd >= 0),

    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Unique constraint: one record per role × country × year × quarter
    CONSTRAINT uq_salary_trends UNIQUE (role_id, country_id, year, quarter)
);


-- -----------------------------------------------------------------------------
-- 2.3 fact_skill_demand
--     504,000 rows. Skill demand by skill × industry × country × year.
--     Largest table — ensure proper indexing before querying.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_skill_demand (
    demand_id       SERIAL          PRIMARY KEY,

    -- Foreign Keys
    skill_id        INT             NOT NULL REFERENCES dim_skill(skill_id)       ON DELETE RESTRICT,
    industry_id     INT             NOT NULL REFERENCES dim_industry(industry_id) ON DELETE RESTRICT,
    country_id      INT             NOT NULL REFERENCES dim_country(country_id)   ON DELETE RESTRICT,

    -- Time Dimension
    year            SMALLINT        NOT NULL CHECK (year BETWEEN 2000 AND 2100),

    -- KPI Fields
    demand_score    NUMERIC(5,2)    CHECK (demand_score BETWEEN 0 AND 100),       -- 0–100 demand index
    mention_count   INT             CHECK (mention_count >= 0),                    -- raw job listing mentions
    growth_pct      NUMERIC(6,2),                                                  -- CANONICAL KPI; NULL for first year

    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Unique constraint: one record per skill × industry × country × year
    CONSTRAINT uq_skill_demand UNIQUE (skill_id, industry_id, country_id, year)
);


-- -----------------------------------------------------------------------------
-- 2.4 fact_ai_disruption
--     11,340 rows. AI disruption scores per role × industry × year.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_ai_disruption (
    disruption_id           SERIAL          PRIMARY KEY,

    -- Foreign Keys
    role_id                 INT             NOT NULL REFERENCES dim_job_role(role_id)    ON DELETE RESTRICT,
    industry_id             INT             NOT NULL REFERENCES dim_industry(industry_id) ON DELETE RESTRICT,

    -- Time Dimension
    year                    SMALLINT        NOT NULL CHECK (year BETWEEN 2000 AND 2100),

    -- KPI Fields
    automation_risk_score   NUMERIC(5,2)    CHECK (automation_risk_score BETWEEN 0 AND 100),   -- CANONICAL KPI
    ai_replacement_index    NUMERIC(5,2)    CHECK (ai_replacement_index BETWEEN 0 AND 100),     -- CANONICAL KPI
    future_safe_score       NUMERIC(5,2)    CHECK (future_safe_score BETWEEN 0 AND 100),        -- CANONICAL KPI; derived = 100 - automation_risk_score

    created_at              TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Unique constraint: one record per role × industry × year
    CONSTRAINT uq_ai_disruption UNIQUE (role_id, industry_id, year)
);


-- =============================================================================
-- 3. INDEXES
--    Optimized for the most common API query patterns defined in the API Blueprint.
-- =============================================================================

-- dim_country
CREATE INDEX IF NOT EXISTS idx_country_region      ON dim_country(region);
CREATE INDEX IF NOT EXISTS idx_country_code        ON dim_country(country_code);

-- dim_industry
CREATE INDEX IF NOT EXISTS idx_industry_sector     ON dim_industry(sector);

-- dim_job_role
CREATE INDEX IF NOT EXISTS idx_role_category       ON dim_job_role(role_category);
CREATE INDEX IF NOT EXISTS idx_role_seniority      ON dim_job_role(seniority_level);
CREATE INDEX IF NOT EXISTS idx_role_remote         ON dim_job_role(is_remote_eligible);

-- dim_skill
CREATE INDEX IF NOT EXISTS idx_skill_category      ON dim_skill(skill_category);
CREATE INDEX IF NOT EXISTS idx_skill_ai_related    ON dim_skill(is_ai_related);
CREATE INDEX IF NOT EXISTS idx_skill_growth        ON dim_skill(growth_pct DESC);

-- fact_job_postings — filtered by date, country, role, industry most often
CREATE INDEX IF NOT EXISTS idx_postings_date       ON fact_job_postings(posting_date);
CREATE INDEX IF NOT EXISTS idx_postings_year       ON fact_job_postings(EXTRACT(YEAR FROM posting_date));
CREATE INDEX IF NOT EXISTS idx_postings_country    ON fact_job_postings(country_id);
CREATE INDEX IF NOT EXISTS idx_postings_role       ON fact_job_postings(role_id);
CREATE INDEX IF NOT EXISTS idx_postings_industry   ON fact_job_postings(industry_id);
CREATE INDEX IF NOT EXISTS idx_postings_remote     ON fact_job_postings(is_remote);
CREATE INDEX IF NOT EXISTS idx_postings_salary     ON fact_job_postings(salary_usd_avg DESC);

-- fact_salary_trends — filtered by year, role, country for trend charts
CREATE INDEX IF NOT EXISTS idx_salary_year         ON fact_salary_trends(year);
CREATE INDEX IF NOT EXISTS idx_salary_role         ON fact_salary_trends(role_id);
CREATE INDEX IF NOT EXISTS idx_salary_country      ON fact_salary_trends(country_id);
CREATE INDEX IF NOT EXISTS idx_salary_growth       ON fact_salary_trends(salary_growth_pct DESC);

-- fact_skill_demand — largest table; composite index critical for performance
CREATE INDEX IF NOT EXISTS idx_demand_year         ON fact_skill_demand(year);
CREATE INDEX IF NOT EXISTS idx_demand_skill        ON fact_skill_demand(skill_id);
CREATE INDEX IF NOT EXISTS idx_demand_industry     ON fact_skill_demand(industry_id);
CREATE INDEX IF NOT EXISTS idx_demand_country      ON fact_skill_demand(country_id);
CREATE INDEX IF NOT EXISTS idx_demand_composite    ON fact_skill_demand(skill_id, industry_id, year);
CREATE INDEX IF NOT EXISTS idx_demand_score        ON fact_skill_demand(demand_score DESC);
CREATE INDEX IF NOT EXISTS idx_demand_growth       ON fact_skill_demand(growth_pct DESC);

-- fact_ai_disruption
CREATE INDEX IF NOT EXISTS idx_disruption_year     ON fact_ai_disruption(year);
CREATE INDEX IF NOT EXISTS idx_disruption_role     ON fact_ai_disruption(role_id);
CREATE INDEX IF NOT EXISTS idx_disruption_industry ON fact_ai_disruption(industry_id);
CREATE INDEX IF NOT EXISTS idx_disruption_risk     ON fact_ai_disruption(automation_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_disruption_safe     ON fact_ai_disruption(future_safe_score DESC);


-- =============================================================================
-- 4. TABLE & COLUMN COMMENTS (for documentation and Power BI tooltips)
-- =============================================================================

-- Tables
COMMENT ON TABLE dim_country         IS 'Reference: 60 countries with regional classification and currency';
COMMENT ON TABLE dim_industry        IS 'Reference: 20 industries with sector grouping and AI adoption index';
COMMENT ON TABLE dim_job_role        IS 'Reference: 81 job roles with seniority, remote eligibility, and AI disruption risk';
COMMENT ON TABLE dim_skill           IS 'Reference: 60 skills with category, AI flag, and YoY demand growth';
COMMENT ON TABLE fact_job_postings   IS 'Fact: 34,020 job posting events with salary and context (2018–2024)';
COMMENT ON TABLE fact_salary_trends  IS 'Fact: 34,020 annual salary trends per role × country (2018–2024)';
COMMENT ON TABLE fact_skill_demand   IS 'Fact: 504,000 skill demand records per skill × industry × country × year';
COMMENT ON TABLE fact_ai_disruption  IS 'Fact: 11,340 AI disruption assessments per role × industry × year';

-- Canonical KPI columns
COMMENT ON COLUMN dim_skill.growth_pct              IS 'CANONICAL KPI — YoY demand growth %; consistent across dim_skill and fact_skill_demand';
COMMENT ON COLUMN dim_job_role.ai_disruption_risk   IS 'CANONICAL KPI — Automation risk score 0–100 at role level';
COMMENT ON COLUMN fact_salary_trends.salary_growth_pct  IS 'CANONICAL KPI — YoY salary growth %; used across backend, frontend, AI summaries';
COMMENT ON COLUMN fact_job_postings.salary_usd_avg      IS 'CANONICAL KPI — Computed average salary in USD';
COMMENT ON COLUMN fact_skill_demand.demand_score        IS 'CANONICAL KPI — Demand index 0–100 based on job listing mention frequency';
COMMENT ON COLUMN fact_skill_demand.growth_pct          IS 'CANONICAL KPI — YoY demand growth %; same name as dim_skill.growth_pct';
COMMENT ON COLUMN fact_ai_disruption.automation_risk_score  IS 'CANONICAL KPI — 0–100 probability of automation within 10 years';
COMMENT ON COLUMN fact_ai_disruption.ai_replacement_index   IS 'CANONICAL KPI — 0–100 composite AI replacement likelihood score';
COMMENT ON COLUMN fact_ai_disruption.future_safe_score      IS 'CANONICAL KPI — Derived: 100 - automation_risk_score; used in UI for safe career display';


-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
