-- =============================================================================
-- 12_cohort_analysis.sql
-- PURPOSE: Cohort-style analysis — grouping entities by their first-observed
--          behavior and tracking how they change over time.
--          Used in: user retention, skill emergence tracking, role lifecycle.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q14: Skill emergence cohort
--      "Group skills by the year they first broke into the top 20 by demand.
--       Track how their demand evolved after that breakout year."
--      This reveals which skills had sustainable growth vs flash-in-the-pan spikes.
-- ---------------------------------------------------------------------------

WITH skill_annual_rank AS (
    -- Rank skills by demand score within each year
    SELECT
        year,
        skill_id,
        skill_name,
        skill_category,
        is_ai_related,
        ROUND(AVG(demand_score), 2) AS avg_demand_score,
        RANK() OVER (
            PARTITION BY year
            ORDER BY AVG(demand_score) DESC
        )                           AS annual_rank
    FROM vw_skill_demand_enriched
    GROUP BY year, skill_id, skill_name, skill_category, is_ai_related
),
first_breakout AS (
    -- Find the first year each skill entered the top 20
    SELECT
        skill_id,
        skill_name,
        skill_category,
        is_ai_related,
        MIN(year)                   AS breakout_year
    FROM skill_annual_rank
    WHERE annual_rank <= 20
    GROUP BY skill_id, skill_name, skill_category, is_ai_related
)
SELECT
    r.skill_name,
    r.skill_category,
    r.is_ai_related,
    f.breakout_year,

    -- Years since breakout (cohort age)
    r.year - f.breakout_year       AS years_since_breakout,
    r.year,
    r.avg_demand_score,
    r.annual_rank,

    -- Is it still in top 20 post-breakout?
    CASE WHEN r.annual_rank <= 20 THEN 'In top 20' ELSE 'Dropped out' END
                                   AS top20_status,

    -- Demand change since breakout year
    r.avg_demand_score - FIRST_VALUE(r.avg_demand_score) OVER (
        PARTITION BY r.skill_id ORDER BY r.year
    )                              AS demand_delta_since_breakout

FROM skill_annual_rank r
JOIN first_breakout    f ON r.skill_id = f.skill_id
WHERE r.year >= f.breakout_year
ORDER BY f.breakout_year, r.skill_name, r.year;


-- ---------------------------------------------------------------------------
-- Q15: Role lifecycle analysis
--      "At what career stage do roles peak in hiring demand and salary?"
--      Groups roles by their career stage trajectory.
-- ---------------------------------------------------------------------------

WITH role_metrics_by_year AS (
    SELECT
        jr.role_name,
        jr.role_category,
        jr.seniority_level,
        EXTRACT(YEAR FROM fp.posting_date)::INT  AS year,
        SUM(fp.posting_count)                    AS total_postings,
        ROUND(AVG(fp.salary_usd_avg), 2)         AS avg_salary
    FROM fact_job_postings fp
    JOIN dim_job_role jr ON fp.role_id = jr.role_id
    GROUP BY jr.role_name, jr.role_category, jr.seniority_level,
             EXTRACT(YEAR FROM fp.posting_date)::INT
),
role_peak AS (
    SELECT
        role_name,
        role_category,
        seniority_level,
        year                                     AS peak_posting_year,
        total_postings                           AS peak_postings,
        avg_salary                               AS peak_salary,
        RANK() OVER (
            PARTITION BY role_name
            ORDER BY total_postings DESC
        )                                        AS posting_rank
    FROM role_metrics_by_year
)
SELECT
    rp.role_name,
    rp.role_category,
    rp.seniority_level,
    rp.peak_posting_year,
    rp.peak_postings,
    rp.peak_salary,

    -- Is the role growing, peaked, or declining?
    CASE
        WHEN rp.peak_posting_year = (SELECT MAX(year) FROM role_metrics_by_year)
            THEN 'Still growing'
        WHEN rp.peak_posting_year >= (SELECT MAX(year) FROM role_metrics_by_year) - 1
            THEN 'Near peak'
        ELSE 'Past peak'
    END                                         AS lifecycle_stage,

    -- Postings in latest year vs peak
    latest.total_postings                       AS latest_year_postings,
    ROUND(
        100.0 * (latest.total_postings - rp.peak_postings)
        / NULLIF(rp.peak_postings, 0),
    2)                                          AS pct_from_peak

FROM role_peak rp
JOIN role_metrics_by_year latest
    ON rp.role_name = latest.role_name
   AND latest.year  = (SELECT MAX(year) FROM role_metrics_by_year)
WHERE rp.posting_rank = 1                       -- only one row per role (the peak year)
ORDER BY rp.peak_postings DESC;


-- ---------------------------------------------------------------------------
-- Q16: Country hiring cohort — which countries entered top 10 in each year?
--      "Track when each country became a major hiring market."
--      This is cohort analysis applied to geography.
-- ---------------------------------------------------------------------------

WITH country_yearly_rank AS (
    SELECT
        posting_year                             AS year,
        country_name,
        region,
        SUM(posting_count)                       AS total_postings,
        RANK() OVER (
            PARTITION BY posting_year
            ORDER BY SUM(posting_count) DESC
        )                                        AS yearly_rank
    FROM vw_job_postings_enriched
    GROUP BY posting_year, country_name, region
),
first_top10_entry AS (
    SELECT
        country_name,
        region,
        MIN(year)                               AS first_top10_year
    FROM country_yearly_rank
    WHERE yearly_rank <= 10
    GROUP BY country_name, region
)
SELECT
    c.country_name,
    c.region,
    f.first_top10_year                          AS cohort_year,
    c.year,
    c.total_postings,
    c.yearly_rank,

    -- Postings growth since first entering top 10
    ROUND(
        100.0 * (c.total_postings -
            FIRST_VALUE(c.total_postings) OVER (
                PARTITION BY c.country_name ORDER BY c.year
            )
        ) / NULLIF(
            FIRST_VALUE(c.total_postings) OVER (
                PARTITION BY c.country_name ORDER BY c.year
            ), 0),
    2)                                          AS growth_since_entry_pct

FROM country_yearly_rank c
JOIN first_top10_entry   f ON c.country_name = f.country_name
WHERE c.year >= f.first_top10_year
ORDER BY f.first_top10_year, c.country_name, c.year;