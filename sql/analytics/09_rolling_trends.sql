-- =============================================================================
-- 09_rolling_trends.sql
-- PURPOSE: Moving averages, lag chains, and trend smoothing.
--          Raw data is noisy. Rolling averages reveal true trends.
--          This is how Bloomberg, Reuters, and financial dashboards work.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q5: 3-year rolling average salary per role (global)
--     "Is salary growth accelerating or slowing down?"
--     Raw YoY is spiky. 3-year rolling average shows the real trend.
-- ---------------------------------------------------------------------------

WITH yearly_role_salary AS (
    SELECT
        year,
        role_name,
        role_category,
        ROUND(AVG(avg_salary_usd), 2) AS avg_salary_usd
    FROM vw_salary_trends_enriched
    GROUP BY year, role_name, role_category
)
SELECT
    year,
    role_name,
    role_category,
    avg_salary_usd,

    -- 3-year rolling average (current + 2 prior years)
    ROUND(AVG(avg_salary_usd) OVER (
        PARTITION BY role_name
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                               AS rolling_3yr_avg_salary,

    -- 3-year rolling growth rate
    ROUND(
        AVG(avg_salary_usd) OVER (
            PARTITION BY role_name
            ORDER BY year
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) -
        AVG(avg_salary_usd) OVER (
            PARTITION BY role_name
            ORDER BY year
            ROWS BETWEEN 5 PRECEDING AND 3 PRECEDING
        ),
    2)                                  AS rolling_momentum_usd

FROM yearly_role_salary
ORDER BY role_name, year;


-- ---------------------------------------------------------------------------
-- Q6: 3-year rolling skill demand (smoothed trend per skill)
--     "Is Python demand genuinely growing or just noisy?"
-- ---------------------------------------------------------------------------

WITH yearly_skill AS (
    SELECT
        year,
        skill_name,
        skill_category,
        is_ai_related,
        ROUND(AVG(demand_score), 2)  AS avg_demand_score,
        SUM(mention_count)           AS total_mentions
    FROM vw_skill_demand_enriched
    GROUP BY year, skill_name, skill_category, is_ai_related
)
SELECT
    year,
    skill_name,
    skill_category,
    is_ai_related,
    avg_demand_score                    AS raw_demand_score,

    -- 3-year rolling average (smoothed)
    ROUND(AVG(avg_demand_score) OVER (
        PARTITION BY skill_name
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                               AS rolling_3yr_demand,

    -- Year-over-year delta (raw)
    avg_demand_score - LAG(avg_demand_score) OVER (
        PARTITION BY skill_name ORDER BY year
    )                                   AS yoy_delta,

    -- 2-year lagged value (for momentum calculation)
    LAG(avg_demand_score, 2) OVER (
        PARTITION BY skill_name ORDER BY year
    )                                   AS demand_2yr_ago,

    -- 2-year momentum: is the skill accelerating?
    ROUND(
        avg_demand_score - LAG(avg_demand_score, 2) OVER (
            PARTITION BY skill_name ORDER BY year
        ),
    2)                                  AS momentum_2yr

FROM yearly_skill
ORDER BY skill_name, year;


-- ---------------------------------------------------------------------------
-- Q7: Lag chain — full salary trajectory with 1yr, 2yr, 3yr lookback
--     "Show me the complete salary history in one row per role-country."
--     This is how time-series feature engineering works in ML pipelines.
-- ---------------------------------------------------------------------------

WITH base AS (
    SELECT
        year,
        role_name,
        country_name,
        ROUND(AVG(avg_salary_usd), 2) AS avg_salary_usd
    FROM vw_salary_trends_enriched
    GROUP BY year, role_name, country_name
)
SELECT
    year,
    role_name,
    country_name,
    avg_salary_usd                      AS salary_current,

    LAG(avg_salary_usd, 1) OVER (
        PARTITION BY role_name, country_name ORDER BY year
    )                                   AS salary_1yr_ago,

    LAG(avg_salary_usd, 2) OVER (
        PARTITION BY role_name, country_name ORDER BY year
    )                                   AS salary_2yr_ago,

    LAG(avg_salary_usd, 3) OVER (
        PARTITION BY role_name, country_name ORDER BY year
    )                                   AS salary_3yr_ago,

    -- 1-year growth
    ROUND(
        100.0 * (avg_salary_usd - LAG(avg_salary_usd, 1) OVER (
            PARTITION BY role_name, country_name ORDER BY year
        )) / NULLIF(LAG(avg_salary_usd, 1) OVER (
            PARTITION BY role_name, country_name ORDER BY year
        ), 0),
    2)                                  AS growth_1yr_pct,

    -- 3-year compound growth (CAGR-style)
    ROUND(
        100.0 * (
            POWER(
                avg_salary_usd / NULLIF(LAG(avg_salary_usd, 3) OVER (
                    PARTITION BY role_name, country_name ORDER BY year
                ), 0),
                1.0/3
            ) - 1
        ),
    2)                                  AS cagr_3yr_pct

FROM base
ORDER BY role_name, country_name, year;