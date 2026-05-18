-- =============================================================================
-- 06_ai_impact_analytics.sql
-- PURPOSE: AI Impact & Disruption KPI queries.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q14: Most at-risk roles (latest year)
--      "Which jobs are most threatened by AI?"
-- ---------------------------------------------------------------------------

SELECT
    role_name,
    role_category,
    seniority_level,
    ROUND(AVG(automation_risk_score), 2)  AS avg_automation_risk,
    ROUND(AVG(ai_replacement_index), 2)   AS avg_ai_replacement,
    ROUND(AVG(future_safe_score), 2)      AS avg_future_safe_score,
    MODE() WITHIN GROUP (ORDER BY risk_tier) AS risk_tier,
    RANK() OVER (
        ORDER BY AVG(automation_risk_score) DESC
    )                                     AS risk_rank
FROM vw_ai_disruption_enriched
WHERE year = (SELECT MAX(year) FROM vw_ai_disruption_enriched)
GROUP BY role_name, role_category, seniority_level
ORDER BY avg_automation_risk DESC
LIMIT 15;


-- ---------------------------------------------------------------------------
-- Q15: Safest careers from AI disruption
--      "Which jobs are most future-proof?"
-- ---------------------------------------------------------------------------

SELECT
    role_name,
    role_category,
    seniority_level,
    is_remote_eligible,
    ROUND(AVG(future_safe_score), 2)      AS avg_future_safe_score,
    ROUND(AVG(automation_risk_score), 2)  AS avg_automation_risk,
    RANK() OVER (
        ORDER BY AVG(future_safe_score) DESC
    )                                     AS safety_rank
FROM vw_ai_disruption_enriched
WHERE year = (SELECT MAX(year) FROM vw_ai_disruption_enriched)
GROUP BY role_name, role_category, seniority_level, is_remote_eligible
ORDER BY avg_future_safe_score DESC
LIMIT 15;


-- ---------------------------------------------------------------------------
-- Q16: AI disruption trend — is automation risk increasing over time?
--      "Is AI getting more dangerous to jobs each year?"
-- ---------------------------------------------------------------------------

SELECT
    year,
    ROUND(AVG(automation_risk_score), 2)  AS global_avg_risk,
    ROUND(AVG(ai_replacement_index), 2)   AS global_avg_replacement,
    ROUND(AVG(future_safe_score), 2)      AS global_avg_safe_score,
    SUM(CASE WHEN risk_tier = 'High'   THEN 1 ELSE 0 END) AS high_risk_role_count,
    SUM(CASE WHEN risk_tier = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_role_count,
    SUM(CASE WHEN risk_tier = 'Low'    THEN 1 ELSE 0 END) AS low_risk_role_count
FROM vw_ai_disruption_enriched
GROUP BY year
ORDER BY year;


-- ---------------------------------------------------------------------------
-- Q17: Industry-level AI disruption index
--      "Which industries are most disrupted by AI?"
-- ---------------------------------------------------------------------------

SELECT
    industry_name,
    sector,
    ROUND(AVG(automation_risk_score), 2)  AS industry_avg_risk,
    ROUND(AVG(ai_replacement_index), 2)   AS industry_avg_replacement,
    ROUND(AVG(ai_adoption_index), 2)      AS ai_adoption_index,
    COUNT(DISTINCT role_id)               AS roles_assessed,
    RANK() OVER (
        ORDER BY AVG(automation_risk_score) DESC
    )                                     AS disruption_rank
FROM vw_ai_disruption_enriched
WHERE year = (SELECT MAX(year) FROM vw_ai_disruption_enriched)
GROUP BY industry_name, sector
ORDER BY industry_avg_risk DESC;