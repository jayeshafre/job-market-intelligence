-- =============================================================================
-- 08_window_functions_advanced.sql
-- PURPOSE: Advanced window function patterns for deep analytical insight.
--          Covers RANK, DENSE_RANK, PERCENT_RANK, CUME_DIST, NTILE,
--          running totals, and frame-based aggregations.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q1: Salary percentile rank for every role × country
--     "Where does a Data Scientist's salary in India rank globally?"
--     PERCENT_RANK returns 0.0 (lowest) to 1.0 (highest)
-- ---------------------------------------------------------------------------

WITH role_country_salary AS (
    SELECT
        role_name,
        country_name,
        region,
        ROUND(AVG(avg_salary_usd), 2) AS avg_salary_usd
    FROM vw_salary_trends_enriched
    WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
    GROUP BY role_name, country_name, region
)
SELECT
    role_name,
    country_name,
    region,
    avg_salary_usd,

    -- What % of all role-country combos earn less than this one
    ROUND(
        PERCENT_RANK() OVER (ORDER BY avg_salary_usd) * 100,
    2)                                          AS global_percentile,

    -- Which quartile: 1 = bottom 25%, 4 = top 25%
    NTILE(4) OVER (ORDER BY avg_salary_usd)     AS salary_quartile,

    -- Cumulative share of all salaries up to this point
    ROUND(
        CUME_DIST() OVER (ORDER BY avg_salary_usd) * 100,
    2)                                          AS cumulative_pct,

    -- Rank within their own region (resets per region)
    RANK() OVER (
        PARTITION BY region
        ORDER BY avg_salary_usd DESC
    )                                           AS rank_within_region

FROM role_country_salary
ORDER BY avg_salary_usd DESC;


-- ---------------------------------------------------------------------------
-- Q2: Running total of job postings (cumulative hiring volume per year)
--     "What is the all-time cumulative hiring count, growing year by year?"
--     This is the 'area under the curve' view recruiters love.
-- ---------------------------------------------------------------------------

WITH yearly AS (
    SELECT
        posting_year                AS year,
        SUM(posting_count)          AS yearly_postings
    FROM vw_job_postings_enriched
    GROUP BY posting_year
)
SELECT
    year,
    yearly_postings,

    -- Running total across all years
    SUM(yearly_postings) OVER (
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                               AS cumulative_postings,

    -- Running average (smoothed hiring level)
    ROUND(AVG(yearly_postings) OVER (
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 0)                           AS running_avg_postings,

    -- Each year's share of all-time total
    ROUND(
        100.0 * yearly_postings
        / SUM(yearly_postings) OVER (),
    2)                              AS pct_of_all_time_total

FROM yearly
ORDER BY year;


-- ---------------------------------------------------------------------------
-- Q3: DENSE_RANK — Top 3 roles per seniority level by salary
--     "What are the top-paying roles for each seniority tier?"
--     DENSE_RANK: ties get the same rank, no gaps (1,1,2 not 1,1,3)
-- ---------------------------------------------------------------------------

WITH role_salary AS (
    SELECT
        seniority_level,
        role_name,
        role_category,
        ROUND(AVG(avg_salary_usd), 2) AS avg_salary_usd
    FROM vw_salary_trends_enriched
    WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
    GROUP BY seniority_level, role_name, role_category
)
SELECT
    seniority_level,
    role_name,
    role_category,
    avg_salary_usd,
    DENSE_RANK() OVER (
        PARTITION BY seniority_level
        ORDER BY avg_salary_usd DESC
    )                               AS rank_in_seniority
FROM role_salary
QUALIFY DENSE_RANK() OVER (         -- filter to top 3 per seniority
    PARTITION BY seniority_level
    ORDER BY avg_salary_usd DESC
) <= 3
ORDER BY seniority_level, rank_in_seniority;

-- NOTE: QUALIFY is a Snowflake/BigQuery feature. In PostgreSQL, wrap in a subquery:
-- SELECT * FROM (...) t WHERE rank_in_seniority <= 3;


-- PostgreSQL-compatible version:
SELECT *
FROM (
    SELECT
        seniority_level,
        role_name,
        role_category,
        avg_salary_usd,
        DENSE_RANK() OVER (
            PARTITION BY seniority_level
            ORDER BY avg_salary_usd DESC
        ) AS rank_in_seniority
    FROM (
        SELECT
            seniority_level,
            role_name,
            role_category,
            ROUND(AVG(avg_salary_usd), 2) AS avg_salary_usd
        FROM vw_salary_trends_enriched
        WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
        GROUP BY seniority_level, role_name, role_category
    ) base
) ranked
WHERE rank_in_seniority <= 3
ORDER BY seniority_level, rank_in_seniority;


-- ---------------------------------------------------------------------------
-- Q4: First value / Last value — salary at start vs end of tracked period
--     "What did this role pay in 2018 vs today, in one row?"
--     Used in before/after comparison cards on dashboards.
-- ---------------------------------------------------------------------------

SELECT DISTINCT
    role_name,
    role_category,
    country_name,

    FIRST_VALUE(ROUND(avg_salary_usd::NUMERIC, 2)) OVER (
        PARTITION BY role_name, country_name
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )                               AS salary_2018,

    LAST_VALUE(ROUND(avg_salary_usd::NUMERIC, 2)) OVER (
        PARTITION BY role_name, country_name
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )                               AS salary_latest,

    -- Absolute USD gain over the full period
    LAST_VALUE(ROUND(avg_salary_usd::NUMERIC, 2)) OVER (
        PARTITION BY role_name, country_name
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) -
    FIRST_VALUE(ROUND(avg_salary_usd::NUMERIC, 2)) OVER (
        PARTITION BY role_name, country_name
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )                               AS total_usd_gain,

    -- % growth across the full period
    ROUND(
        100.0 * (
            LAST_VALUE(avg_salary_usd) OVER (
                PARTITION BY role_name, country_name
                ORDER BY year
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) -
            FIRST_VALUE(avg_salary_usd) OVER (
                PARTITION BY role_name, country_name
                ORDER BY year
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            )
        ) / NULLIF(
            FIRST_VALUE(avg_salary_usd) OVER (
                PARTITION BY role_name, country_name
                ORDER BY year
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ), 0),
    2)                              AS total_growth_pct

FROM vw_salary_trends_enriched
ORDER BY total_growth_pct DESC NULLS LAST;