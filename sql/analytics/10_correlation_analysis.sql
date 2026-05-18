-- =============================================================================
-- 10_correlation_analysis.sql
-- PURPOSE: Statistical relationship analysis between KPIs.
--          Answers: does AI adoption CAUSE higher salaries?
--          Does automation risk CORRELATE with lower hiring?
--          This is the analytical layer that drives AI chatbot answers.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q8: Correlation — AI adoption index vs average salary by industry
--     "Do more AI-adopted industries pay better?"
--     Uses PostgreSQL built-in CORR() function.
--     Result: +1.0 = perfect positive, -1.0 = perfect negative, 0 = no relationship
-- ---------------------------------------------------------------------------

SELECT
    ROUND(CORR(ai_adoption_index, avg_salary_usd)::NUMERIC, 4)
                                        AS corr_ai_adoption_vs_salary,

    -- Interpretation bucket
    CASE
        WHEN ABS(CORR(ai_adoption_index, avg_salary_usd)) >= 0.7 THEN 'Strong'
        WHEN ABS(CORR(ai_adoption_index, avg_salary_usd)) >= 0.4 THEN 'Moderate'
        ELSE 'Weak'
    END                                 AS correlation_strength,

    CASE
        WHEN CORR(ai_adoption_index, avg_salary_usd) > 0 THEN 'Positive'
        ELSE 'Negative'
    END                                 AS correlation_direction,

    COUNT(*)                            AS data_points

FROM (
    SELECT
        di.ai_adoption_index,
        AVG(fp.salary_usd_avg) AS avg_salary_usd
    FROM fact_job_postings fp
    JOIN dim_industry di ON fp.industry_id = di.industry_id
    GROUP BY di.industry_id, di.ai_adoption_index
) industry_stats;


-- ---------------------------------------------------------------------------
-- Q9: Correlation — automation risk vs salary across all roles
--     "Do high-risk roles earn more or less?"
--     Classic question: does AI danger come with a pay premium?
-- ---------------------------------------------------------------------------

SELECT
    ROUND(CORR(avg_automation_risk, avg_salary_usd)::NUMERIC, 4)
                                        AS corr_risk_vs_salary,
    ROUND(CORR(avg_future_safe_score, avg_salary_usd)::NUMERIC, 4)
                                        AS corr_safety_vs_salary,
    COUNT(*)                            AS roles_analyzed

FROM (
    SELECT
        jr.role_id,
        AVG(ad.automation_risk_score)   AS avg_automation_risk,
        AVG(ad.future_safe_score)       AS avg_future_safe_score,
        AVG(fp.salary_usd_avg)          AS avg_salary_usd
    FROM dim_job_role jr
    JOIN fact_ai_disruption  ad ON jr.role_id = ad.role_id
    JOIN fact_job_postings   fp ON jr.role_id = fp.role_id
    GROUP BY jr.role_id
) role_stats;


-- ---------------------------------------------------------------------------
-- Q10: Scatter data — skill growth vs demand score (for scatter plot chart)
--      "Do high-demand skills always grow fast, or are some peaking?"
--      Output feeds a scatter plot: x = demand_score, y = growth_pct
--      Quadrants: Stars (high demand + high growth), Cash Cows (high demand + low growth),
--                 Rising (low demand + high growth), Declining (low demand + low growth)
-- ---------------------------------------------------------------------------

WITH skill_stats AS (
    SELECT
        skill_name,
        skill_category,
        is_ai_related,
        ROUND(AVG(demand_score), 2)      AS avg_demand_score,
        ROUND(AVG(yearly_growth_pct), 2) AS avg_growth_pct
    FROM vw_skill_demand_enriched
    WHERE year >= (SELECT MAX(year) FROM vw_skill_demand_enriched) - 2
      AND yearly_growth_pct IS NOT NULL
    GROUP BY skill_name, skill_category, is_ai_related
),
medians AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY avg_demand_score) AS median_demand,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY avg_growth_pct)   AS median_growth
    FROM skill_stats
)
SELECT
    s.skill_name,
    s.skill_category,
    s.is_ai_related,
    s.avg_demand_score,
    s.avg_growth_pct,

    -- BCG-style quadrant classification
    CASE
        WHEN s.avg_demand_score >= m.median_demand
         AND s.avg_growth_pct   >= m.median_growth THEN 'Star'         -- high demand, high growth
        WHEN s.avg_demand_score >= m.median_demand
         AND s.avg_growth_pct   <  m.median_growth THEN 'Cash Cow'     -- high demand, slowing
        WHEN s.avg_demand_score <  m.median_demand
         AND s.avg_growth_pct   >= m.median_growth THEN 'Rising'       -- low demand, fast growing
        ELSE                                             'Declining'    -- low demand, slow growth
    END                                 AS skill_quadrant

FROM skill_stats s
CROSS JOIN medians m
ORDER BY avg_demand_score DESC;


-- ---------------------------------------------------------------------------
-- Q11: Industry-level analysis — AI adoption vs hiring growth vs salary
--      "The full picture: does more AI adoption mean more jobs and higher pay?"
--      Multi-metric correlation table — the kind senior analysts build.
-- ---------------------------------------------------------------------------

WITH industry_metrics AS (
    SELECT
        di.industry_name,
        di.sector,
        di.ai_adoption_index,

        -- Hiring volume
        SUM(fp.posting_count)                       AS total_postings,

        -- Salary
        ROUND(AVG(fp.salary_usd_avg), 2)            AS avg_salary_usd,

        -- AI risk (average across roles in that industry)
        ROUND(AVG(ad.automation_risk_score), 2)     AS avg_ai_risk

    FROM dim_industry di
    JOIN fact_job_postings  fp ON di.industry_id = fp.industry_id
    JOIN fact_ai_disruption ad ON di.industry_id = ad.industry_id
    GROUP BY di.industry_id, di.industry_name, di.sector, di.ai_adoption_index
)
SELECT
    industry_name,
    sector,
    ai_adoption_index,
    total_postings,
    avg_salary_usd,
    avg_ai_risk,

    -- Rank each dimension independently
    RANK() OVER (ORDER BY ai_adoption_index DESC)  AS ai_adoption_rank,
    RANK() OVER (ORDER BY total_postings DESC)      AS hiring_volume_rank,
    RANK() OVER (ORDER BY avg_salary_usd DESC)      AS salary_rank,
    RANK() OVER (ORDER BY avg_ai_risk DESC)         AS risk_rank,

    -- Composite opportunity score (lower rank = better, so invert)
    ROUND(
        (
            (COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY ai_adoption_index DESC)) +
            (COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY total_postings DESC))    +
            (COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY avg_salary_usd DESC))
        ) / 3.0,
    1)                                              AS opportunity_score

FROM industry_metrics
ORDER BY opportunity_score DESC;