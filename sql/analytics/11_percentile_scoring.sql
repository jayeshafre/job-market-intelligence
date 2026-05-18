-- =============================================================================
-- 11_percentile_scoring.sql
-- PURPOSE: Composite KPI scoring system.
--          Converts raw metrics into normalized 0–100 scores, then
--          combines them into a weighted composite score per role/skill.
--          This powers the AI chatbot's ranking answers and the
--          "Best career for you" feature.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q12: Career opportunity score — composite rank for every role
--      Formula: weighted average of salary score + safety score + demand score
--      Weights: Salary 40% + Future Safety 35% + Hiring Demand 25%
--      Output: one score per role, 0–100, comparable across everything
-- ---------------------------------------------------------------------------

WITH role_raw_metrics AS (
    -- Step 1: gather raw KPIs per role (latest year)
    SELECT
        jr.role_id,
        jr.role_name,
        jr.role_category,
        jr.seniority_level,
        jr.is_remote_eligible,

        COALESCE(AVG(st.avg_salary_usd), 0)             AS avg_salary,
        COALESCE(AVG(ad.future_safe_score), 50)         AS avg_safety_score,
        COALESCE(AVG(ad.automation_risk_score), 50)     AS avg_risk_score,
        COALESCE(SUM(fp.posting_count), 0)              AS total_postings

    FROM dim_job_role jr
    LEFT JOIN fact_salary_trends   st ON jr.role_id = st.role_id
          AND st.year = (SELECT MAX(year) FROM fact_salary_trends)
    LEFT JOIN fact_ai_disruption   ad ON jr.role_id = ad.role_id
          AND ad.year = (SELECT MAX(year) FROM fact_ai_disruption)
    LEFT JOIN fact_job_postings    fp ON jr.role_id = fp.role_id
    GROUP BY jr.role_id, jr.role_name, jr.role_category,
             jr.seniority_level, jr.is_remote_eligible
),
normalized AS (
    -- Step 2: min-max normalize each metric to 0–100
    -- Formula: (value - min) / (max - min) * 100
    SELECT
        role_id,
        role_name,
        role_category,
        seniority_level,
        is_remote_eligible,
        avg_salary,
        avg_safety_score,
        avg_risk_score,
        total_postings,

        ROUND(
            100.0 * (avg_salary - MIN(avg_salary) OVER ())
            / NULLIF(MAX(avg_salary) OVER () - MIN(avg_salary) OVER (), 0),
        2)                          AS salary_score_normalized,

        -- Safety is already 0–100, use directly
        ROUND(avg_safety_score, 2)  AS safety_score_normalized,

        ROUND(
            100.0 * (total_postings - MIN(total_postings) OVER ())
            / NULLIF(MAX(total_postings) OVER () - MIN(total_postings) OVER (), 0),
        2)                          AS demand_score_normalized
    FROM role_raw_metrics
)
SELECT
    role_id,
    role_name,
    role_category,
    seniority_level,
    is_remote_eligible,
    ROUND(avg_salary, 2)                AS avg_salary_usd,
    ROUND(avg_safety_score, 2)          AS future_safe_score,
    ROUND(avg_risk_score, 2)            AS automation_risk_score,
    total_postings,
    salary_score_normalized,
    safety_score_normalized,
    demand_score_normalized,

    -- Step 3: weighted composite score
    -- Salary 40% + Safety 35% + Demand 25%
    ROUND(
        (salary_score_normalized * 0.40) +
        (safety_score_normalized * 0.35) +
        (demand_score_normalized * 0.25),
    2)                                  AS career_opportunity_score,

    -- Final rank
    RANK() OVER (
        ORDER BY
            (salary_score_normalized * 0.40) +
            (safety_score_normalized * 0.35) +
            (demand_score_normalized * 0.25)
        DESC
    )                                   AS career_rank

FROM normalized
ORDER BY career_opportunity_score DESC;


-- ---------------------------------------------------------------------------
-- Q13: Skill investment score — which skill is worth learning right now?
--      Formula: Demand score 40% + Growth velocity 35% + AI relevance 25%
--      Answers the chatbot question: "Which skill should I learn next?"
-- ---------------------------------------------------------------------------

WITH skill_raw AS (
    SELECT
        sk.skill_id,
        sk.skill_name,
        sk.skill_category,
        sk.is_ai_related,
        COALESCE(AVG(sd.demand_score), 0)        AS avg_demand_score,
        COALESCE(AVG(sd.growth_pct), 0)          AS avg_growth_pct
    FROM dim_skill sk
    LEFT JOIN fact_skill_demand sd ON sk.skill_id = sd.skill_id
           AND sd.year >= (SELECT MAX(year) FROM fact_skill_demand) - 2
    GROUP BY sk.skill_id, sk.skill_name, sk.skill_category, sk.is_ai_related
),
normalized AS (
    SELECT
        skill_id,
        skill_name,
        skill_category,
        is_ai_related,
        avg_demand_score,
        avg_growth_pct,

        -- Normalize demand: 0–100
        ROUND(
            100.0 * (avg_demand_score - MIN(avg_demand_score) OVER ())
            / NULLIF(MAX(avg_demand_score) OVER () - MIN(avg_demand_score) OVER (), 0),
        2)                              AS demand_norm,

        -- Normalize growth: 0–100
        ROUND(
            100.0 * (avg_growth_pct - MIN(avg_growth_pct) OVER ())
            / NULLIF(MAX(avg_growth_pct) OVER () - MIN(avg_growth_pct) OVER (), 0),
        2)                              AS growth_norm,

        -- AI relevance: binary bonus (25 = AI, 0 = not)
        CASE WHEN is_ai_related THEN 25.0 ELSE 0.0 END AS ai_bonus
    FROM skill_raw
)
SELECT
    skill_id,
    skill_name,
    skill_category,
    is_ai_related,
    ROUND(avg_demand_score, 2)          AS raw_demand_score,
    ROUND(avg_growth_pct, 2)            AS raw_growth_pct,

    -- Weighted composite score
    ROUND(
        (demand_norm * 0.40) +
        (growth_norm * 0.35) +
        (ai_bonus    * 1.00),           -- AI bonus added directly (max 25pts)
    2)                                  AS skill_investment_score,

    RANK() OVER (
        ORDER BY
            (demand_norm * 0.40) + (growth_norm * 0.35) + (ai_bonus * 1.00)
        DESC
    )                                   AS learn_priority_rank

FROM normalized
ORDER BY skill_investment_score DESC;