-- =============================================================================
-- 05_skill_analytics.sql
-- PURPOSE: Skill Intelligence KPI queries.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q10: Top 15 skills by demand score (latest year)
--      "Which skills are most in demand right now?"
-- ---------------------------------------------------------------------------

SELECT
    skill_name,
    skill_category,
    is_ai_related,
    ROUND(AVG(demand_score), 2)       AS avg_demand_score,
    SUM(mention_count)                AS total_mentions,
    ROUND(AVG(yearly_growth_pct), 2)  AS avg_growth_pct,
    RANK() OVER (
        ORDER BY AVG(demand_score) DESC
    )                                 AS demand_rank
FROM vw_skill_demand_enriched
WHERE year = (SELECT MAX(year) FROM vw_skill_demand_enriched)
GROUP BY skill_name, skill_category, is_ai_related
ORDER BY avg_demand_score DESC
LIMIT 15;


-- ---------------------------------------------------------------------------
-- Q11: Fastest growing skills (by YoY growth %)
--      "Which skills are rising fastest?"
-- ---------------------------------------------------------------------------

WITH skill_growth AS (
    SELECT
        skill_name,
        skill_category,
        is_ai_related,
        year,
        ROUND(AVG(demand_score), 2)      AS avg_demand_score,
        ROUND(AVG(yearly_growth_pct), 2) AS avg_growth_pct
    FROM vw_skill_demand_enriched
    GROUP BY skill_name, skill_category, is_ai_related, year
)
SELECT
    skill_name,
    skill_category,
    is_ai_related,
    avg_demand_score,
    avg_growth_pct,
    RANK() OVER (ORDER BY avg_growth_pct DESC NULLS LAST) AS growth_rank
FROM skill_growth
WHERE year = (SELECT MAX(year) FROM vw_skill_demand_enriched)
  AND avg_growth_pct IS NOT NULL
ORDER BY avg_growth_pct DESC
LIMIT 15;


-- ---------------------------------------------------------------------------
-- Q12: AI vs non-AI skill demand share, trending by year
--      "Is demand for AI skills growing faster than traditional skills?"
-- ---------------------------------------------------------------------------

SELECT
    year,
    SUM(CASE WHEN is_ai_related THEN mention_count ELSE 0 END)     AS ai_skill_mentions,
    SUM(CASE WHEN NOT is_ai_related THEN mention_count ELSE 0 END)  AS non_ai_skill_mentions,
    SUM(mention_count)                                               AS total_mentions,
    ROUND(
        100.0 * SUM(CASE WHEN is_ai_related THEN mention_count ELSE 0 END)
        / NULLIF(SUM(mention_count), 0),
    2)                                                               AS ai_skill_share_pct
FROM vw_skill_demand_enriched
GROUP BY year
ORDER BY year;


-- ---------------------------------------------------------------------------
-- Q13: Skill demand heatmap — top skills × top industries
--      "Which skills matter most in which industries?"
-- ---------------------------------------------------------------------------

SELECT
    skill_name,
    skill_category,
    industry_name,
    ROUND(AVG(demand_score), 2) AS avg_demand_score
FROM vw_skill_demand_enriched
WHERE year = (SELECT MAX(year) FROM vw_skill_demand_enriched)
  AND skill_name IN (
      SELECT skill_name
      FROM mv_skill_demand_yearly
      WHERE year = (SELECT MAX(year) FROM mv_skill_demand_yearly)
      ORDER BY demand_rank
      LIMIT 10
  )
GROUP BY skill_name, skill_category, industry_name
ORDER BY skill_name, avg_demand_score DESC;