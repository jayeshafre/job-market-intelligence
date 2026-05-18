-- =============================================================================
-- 02_materialized_views.sql
-- PURPOSE: Pre-aggregated materialized views for fast API + dashboard queries.
--          Refresh with: REFRESH MATERIALIZED VIEW CONCURRENTLY <view_name>;
-- =============================================================================


-- ---------------------------------------------------------------------------
-- MV1: mv_monthly_hiring_volume
--      Monthly job posting counts by country and industry.
--      Powers: Hiring trend line charts, country demand maps.
-- ---------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_hiring_volume AS
SELECT
    posting_year,
    posting_month,
    country_id,
    country_name,
    region,
    industry_id,
    industry_name,
    sector,

    SUM(posting_count)              AS total_postings,
    COUNT(DISTINCT posting_id)      AS unique_listings,
    SUM(CASE WHEN is_remote THEN posting_count ELSE 0 END) AS remote_postings,

    -- Remote ratio as a percentage
    ROUND(
        100.0 * SUM(CASE WHEN is_remote THEN posting_count ELSE 0 END)
        / NULLIF(SUM(posting_count), 0),
    2) AS remote_pct,

    AVG(salary_usd_avg)::NUMERIC(12,2) AS avg_salary_usd

FROM vw_job_postings_enriched
GROUP BY
    posting_year, posting_month,
    country_id, country_name, region,
    industry_id, industry_name, sector
WITH DATA;

CREATE UNIQUE INDEX ON mv_monthly_hiring_volume
    (posting_year, posting_month, country_id, industry_id);


-- ---------------------------------------------------------------------------
-- MV2: mv_yearly_salary_by_role
--      Annual median + average salary per role, country, and seniority.
--      Powers: Salary comparison bars, YoY salary growth charts.
-- ---------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_yearly_salary_by_role AS
SELECT
    st.year,
    st.role_id,
    st.role_name,
    st.role_category,
    st.seniority_level,
    st.country_id,
    st.country_name,
    st.region,

    ROUND(AVG(st.avg_salary_usd),    2) AS avg_salary_usd,
    ROUND(AVG(st.median_salary_usd), 2) AS median_salary_usd,
    ROUND(AVG(st.salary_growth_pct), 2) AS avg_salary_growth_pct,

    -- Year-over-year delta using window function
    ROUND(
        AVG(st.avg_salary_usd) - LAG(AVG(st.avg_salary_usd))
            OVER (PARTITION BY st.role_id, st.country_id ORDER BY st.year),
    2) AS salary_yoy_delta_usd

FROM vw_salary_trends_enriched st
GROUP BY
    st.year, st.role_id, st.role_name, st.role_category,
    st.seniority_level, st.country_id, st.country_name, st.region
WITH DATA;

CREATE UNIQUE INDEX ON mv_yearly_salary_by_role
    (year, role_id, country_id);


-- ---------------------------------------------------------------------------
-- MV3: mv_skill_demand_yearly
--      Annual skill demand aggregated across all countries + industries.
--      Powers: Top skills bar charts, skill growth trend lines.
-- ---------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_demand_yearly AS
SELECT
    year,
    skill_id,
    skill_name,
    skill_category,
    is_ai_related,

    ROUND(AVG(demand_score),  2) AS avg_demand_score,
    SUM(mention_count)           AS total_mentions,
    ROUND(AVG(yearly_growth_pct), 2) AS avg_growth_pct,

    -- Rank skills by demand score within each year
    RANK() OVER (
        PARTITION BY year
        ORDER BY AVG(demand_score) DESC
    ) AS demand_rank,

    -- Rank skills by growth within each year
    RANK() OVER (
        PARTITION BY year
        ORDER BY AVG(yearly_growth_pct) DESC NULLS LAST
    ) AS growth_rank

FROM vw_skill_demand_enriched
GROUP BY
    year, skill_id, skill_name, skill_category, is_ai_related
WITH DATA;

CREATE UNIQUE INDEX ON mv_skill_demand_yearly (year, skill_id);


-- ---------------------------------------------------------------------------
-- MV4: mv_ai_disruption_by_role
--      Latest year AI disruption scores per role, averaged across industries.
--      Powers: Risk scorecards, future-safe career rankings.
-- ---------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ai_disruption_by_role AS
SELECT
    year,
    role_id,
    role_name,
    role_category,
    seniority_level,
    is_remote_eligible,

    ROUND(AVG(automation_risk_score), 2) AS avg_automation_risk,
    ROUND(AVG(ai_replacement_index),  2) AS avg_ai_replacement,
    ROUND(AVG(future_safe_score),     2) AS avg_future_safe_score,

    -- Most common risk tier across industries
    MODE() WITHIN GROUP (ORDER BY risk_tier) AS dominant_risk_tier,

    -- Count of industries where this role is high-risk
    SUM(CASE WHEN risk_tier = 'High' THEN 1 ELSE 0 END) AS high_risk_industry_count

FROM vw_ai_disruption_enriched
GROUP BY
    year, role_id, role_name, role_category,
    seniority_level, is_remote_eligible
WITH DATA;

CREATE UNIQUE INDEX ON mv_ai_disruption_by_role (year, role_id);