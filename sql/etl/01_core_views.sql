-- =============================================================================
-- 01_core_views.sql
-- PURPOSE: Enriched base views — fact tables joined with all dimensions.
--          All analytics queries build on these. Never query raw tables directly.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- V1: vw_job_postings_enriched
--     fact_job_postings + all 3 dimensions joined.
--     This is the most important view — almost every KPI traces back to it.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW vw_job_postings_enriched AS
SELECT
    -- Posting identifiers
    fp.posting_id,
    fp.posting_date,
    EXTRACT(YEAR  FROM fp.posting_date)::INT   AS posting_year,
    EXTRACT(MONTH FROM fp.posting_date)::INT   AS posting_month,
    EXTRACT(QUARTER FROM fp.posting_date)::INT AS posting_quarter,

    -- Role dimension
    jr.role_id,
    jr.role_name,
    jr.role_category,
    jr.seniority_level,
    jr.is_remote_eligible,
    jr.ai_disruption_risk,

    -- Country dimension
    dc.country_id,
    dc.country_name,
    dc.region,
    dc.sub_region,
    dc.currency_code,

    -- Industry dimension
    di.industry_id,
    di.industry_name,
    di.sector,
    di.ai_adoption_index,

    -- Salary KPIs
    fp.salary_usd_min,
    fp.salary_usd_max,
    fp.salary_usd_avg,                          -- CANONICAL KPI
    fp.is_remote,
    fp.experience_years_req,
    fp.posting_count

FROM fact_job_postings fp
JOIN dim_job_role  jr ON fp.role_id     = jr.role_id
JOIN dim_country   dc ON fp.country_id  = dc.country_id
JOIN dim_industry  di ON fp.industry_id = di.industry_id;


-- ---------------------------------------------------------------------------
-- V2: vw_salary_trends_enriched
--     fact_salary_trends + role + country dimensions.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW vw_salary_trends_enriched AS
SELECT
    st.trend_id,
    st.year,

    -- Role dimension
    jr.role_id,
    jr.role_name,
    jr.role_category,
    jr.seniority_level,

    -- Country dimension
    dc.country_id,
    dc.country_name,
    dc.region,
    dc.currency_code,

    -- Salary KPIs
    st.avg_salary_usd,
    st.median_salary_usd,
    st.salary_growth_pct                        -- CANONICAL KPI

FROM fact_salary_trends st
JOIN dim_job_role jr ON st.role_id    = jr.role_id
JOIN dim_country  dc ON st.country_id = dc.country_id;


-- ---------------------------------------------------------------------------
-- V3: vw_skill_demand_enriched
--     fact_skill_demand + skill + industry + country dimensions.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW vw_skill_demand_enriched AS
SELECT
    sd.demand_id,
    sd.year,

    -- Skill dimension
    sk.skill_id,
    sk.skill_name,
    sk.skill_category,
    sk.is_ai_related,
    sk.growth_pct          AS skill_overall_growth_pct,

    -- Industry dimension
    di.industry_id,
    di.industry_name,
    di.sector,
    di.ai_adoption_index,

    -- Country dimension
    dc.country_id,
    dc.country_name,
    dc.region,

    -- Demand KPIs
    sd.demand_score,                            -- CANONICAL KPI
    sd.mention_count,
    sd.growth_pct          AS yearly_growth_pct -- CANONICAL KPI

FROM fact_skill_demand sd
JOIN dim_skill    sk ON sd.skill_id    = sk.skill_id
JOIN dim_industry di ON sd.industry_id = di.industry_id
JOIN dim_country  dc ON sd.country_id  = dc.country_id;


-- ---------------------------------------------------------------------------
-- V4: vw_ai_disruption_enriched
--     fact_ai_disruption + role + industry dimensions.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW vw_ai_disruption_enriched AS
SELECT
    ad.disruption_id,
    ad.year,

    -- Role dimension
    jr.role_id,
    jr.role_name,
    jr.role_category,
    jr.seniority_level,
    jr.is_remote_eligible,

    -- Industry dimension
    di.industry_id,
    di.industry_name,
    di.sector,
    di.ai_adoption_index,

    -- AI KPIs
    ad.automation_risk_score,                   -- CANONICAL KPI
    ad.ai_replacement_index,                    -- CANONICAL KPI
    ad.future_safe_score,                       -- CANONICAL KPI

    -- Derived risk tier (computed column — no storage cost)
    CASE
        WHEN ad.automation_risk_score >= 70 THEN 'High'
        WHEN ad.automation_risk_score >= 40 THEN 'Medium'
        ELSE 'Low'
    END AS risk_tier

FROM fact_ai_disruption ad
JOIN dim_job_role  jr ON ad.role_id     = jr.role_id
JOIN dim_industry  di ON ad.industry_id = di.industry_id;