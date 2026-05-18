-- =============================================================================
-- 04_salary_analytics.sql
-- PURPOSE: Salary Intelligence KPI queries.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q6: Median salary by role (latest year, global)
--     "What does each role pay on average?"
-- ---------------------------------------------------------------------------

SELECT
    role_name,
    role_category,
    seniority_level,
    ROUND(AVG(median_salary_usd), 2)  AS median_salary_usd,
    ROUND(AVG(avg_salary_usd), 2)     AS avg_salary_usd,
    ROUND(AVG(salary_growth_pct), 2)  AS avg_growth_pct,
    RANK() OVER (
        ORDER BY AVG(median_salary_usd) DESC
    )                                 AS salary_rank
FROM vw_salary_trends_enriched
WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
GROUP BY role_name, role_category, seniority_level
ORDER BY median_salary_usd DESC;


-- ---------------------------------------------------------------------------
-- Q7: Country salary comparison for a given role
--     "Where in the world pays the most for Data Engineers?"
-- ---------------------------------------------------------------------------

SELECT
    country_name,
    region,
    ROUND(AVG(avg_salary_usd), 2)     AS avg_salary_usd,
    ROUND(AVG(median_salary_usd), 2)  AS median_salary_usd,
    NTILE(4) OVER (
        ORDER BY AVG(avg_salary_usd)
    )                                 AS salary_quartile,   -- 4 = top 25%
    RANK() OVER (
        ORDER BY AVG(avg_salary_usd) DESC
    )                                 AS country_rank
FROM vw_salary_trends_enriched
WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
  AND role_name = 'Data Engineer'       -- parameterize in FastAPI
GROUP BY country_name, region
ORDER BY avg_salary_usd DESC;


-- ---------------------------------------------------------------------------
-- Q8: Salary growth trend (top 5 fastest-growing roles)
--     "Which roles have seen the biggest salary increases?"
-- ---------------------------------------------------------------------------

WITH role_growth AS (
    SELECT
        role_name,
        role_category,
        ROUND(AVG(salary_growth_pct), 2)    AS avg_growth_pct,
        ROUND(MIN(avg_salary_usd), 2)       AS salary_2018,
        ROUND(MAX(avg_salary_usd), 2)       AS salary_latest,
        ROUND(MAX(avg_salary_usd) - MIN(avg_salary_usd), 2) AS total_usd_gain
    FROM vw_salary_trends_enriched
    GROUP BY role_name, role_category
)
SELECT
    role_name,
    role_category,
    avg_growth_pct,
    salary_2018,
    salary_latest,
    total_usd_gain,
    RANK() OVER (ORDER BY avg_growth_pct DESC) AS growth_rank
FROM role_growth
ORDER BY avg_growth_pct DESC NULLS LAST
LIMIT 10;


-- ---------------------------------------------------------------------------
-- Q9: Experience premium — how much extra does seniority pay?
--     "What is the salary jump from Junior → Mid → Senior?"
-- ---------------------------------------------------------------------------

SELECT
    seniority_level,
    ROUND(AVG(median_salary_usd), 2)      AS median_salary_usd,
    ROUND(
        AVG(median_salary_usd) / NULLIF(
            FIRST_VALUE(AVG(median_salary_usd)) OVER (
                ORDER BY
                    CASE seniority_level
                        WHEN 'Entry'     THEN 1
                        WHEN 'Mid'       THEN 2
                        WHEN 'Senior'    THEN 3
                        WHEN 'Director'  THEN 4
                        WHEN 'C-Suite'   THEN 5
                    END
            ),
        0),
    2)                                    AS premium_multiplier  -- 1.0 = baseline
FROM vw_salary_trends_enriched
WHERE year = (SELECT MAX(year) FROM vw_salary_trends_enriched)
GROUP BY seniority_level
ORDER BY
    CASE seniority_level
        WHEN 'Entry'    THEN 1
        WHEN 'Mid'      THEN 2
        WHEN 'Senior'   THEN 3
        WHEN 'Director' THEN 4
        WHEN 'C-Suite'  THEN 5
    END;