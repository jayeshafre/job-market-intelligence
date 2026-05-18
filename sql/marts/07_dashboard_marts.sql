-- =============================================================================
-- 07_dashboard_marts.sql
-- PURPOSE: Final mart views — one view per dashboard widget.
--          FastAPI endpoints call these directly. Zero joins needed.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- MART 1: Executive summary card (single row — the homepage KPI strip)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW mart_executive_summary AS
SELECT
    (SELECT COUNT(DISTINCT country_id)              FROM fact_job_postings)  AS countries_tracked,
    (SELECT COUNT(DISTINCT role_id)                 FROM dim_job_role)       AS roles_tracked,
    (SELECT COUNT(DISTINCT skill_id)                FROM dim_skill)          AS skills_tracked,
    (SELECT SUM(posting_count)                      FROM fact_job_postings)  AS total_job_postings,
    (SELECT ROUND(AVG(salary_usd_avg), 0)           FROM fact_job_postings)  AS global_avg_salary_usd,
    (SELECT ROUND(AVG(automation_risk_score), 1)    FROM fact_ai_disruption) AS global_avg_ai_risk,
    (SELECT COUNT(*) FILTER (WHERE is_ai_related)   FROM dim_skill)          AS ai_skills_count,
    (SELECT MAX(posting_date)                       FROM fact_job_postings)  AS data_through_date;


-- ---------------------------------------------------------------------------
-- MART 2: Hiring trend line (for the main trend chart)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW mart_hiring_trend AS
SELECT
    posting_year                        AS year,
    SUM(posting_count)                  AS total_postings,
    ROUND(AVG(salary_usd_avg), 2)       AS avg_salary_usd,
    ROUND(
        100.0 * SUM(CASE WHEN is_remote THEN posting_count ELSE 0 END)
        / NULLIF(SUM(posting_count), 0),
    2)                                  AS remote_pct,
    LAG(SUM(posting_count)) OVER (ORDER BY posting_year) AS prev_year_postings,
    ROUND(
        100.0 * (SUM(posting_count) - LAG(SUM(posting_count)) OVER (ORDER BY posting_year))
        / NULLIF(LAG(SUM(posting_count)) OVER (ORDER BY posting_year), 0),
    2)                                  AS yoy_growth_pct
FROM vw_job_postings_enriched
GROUP BY posting_year
ORDER BY posting_year;


-- ---------------------------------------------------------------------------
-- MART 3: Top skills leaderboard (for the skills ranking table)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW mart_top_skills AS
SELECT
    skill_name,
    skill_category,
    is_ai_related,
    avg_demand_score,
    total_mentions,
    avg_growth_pct,
    demand_rank,
    growth_rank
FROM mv_skill_demand_yearly
WHERE year = (SELECT MAX(year) FROM mv_skill_demand_yearly)
ORDER BY demand_rank
LIMIT 20;


-- ---------------------------------------------------------------------------
-- MART 4: AI risk leaderboard (for the risk scorecard)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW mart_ai_risk_leaderboard AS
SELECT
    role_name,
    role_category,
    seniority_level,
    avg_automation_risk,
    avg_future_safe_score,
    dominant_risk_tier,
    RANK() OVER (ORDER BY avg_automation_risk DESC) AS risk_rank
FROM mv_ai_disruption_by_role
WHERE year = (SELECT MAX(year) FROM mv_ai_disruption_by_role)
ORDER BY avg_automation_risk DESC;


-- ---------------------------------------------------------------------------
-- MART 5: Country salary map (for the choropleth world map widget)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW mart_country_salary_map AS
SELECT
    dc.country_name,
    dc.country_code,
    dc.region,
    dc.sub_region,
    ROUND(AVG(fp.salary_usd_avg), 2)    AS avg_salary_usd,
    SUM(fp.posting_count)               AS total_postings,
    ROUND(
        100.0 * SUM(CASE WHEN fp.is_remote THEN fp.posting_count ELSE 0 END)
        / NULLIF(SUM(fp.posting_count), 0),
    2)                                  AS remote_pct
FROM fact_job_postings fp
JOIN dim_country dc ON fp.country_id = dc.country_id
WHERE EXTRACT(YEAR FROM fp.posting_date) =
      (SELECT MAX(EXTRACT(YEAR FROM posting_date)) FROM fact_job_postings)
GROUP BY dc.country_name, dc.country_code, dc.region, dc.sub_region
ORDER BY avg_salary_usd DESC;