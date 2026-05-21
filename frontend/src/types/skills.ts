// ─────────────────────────────────────────
// types/skills.ts
// Field names mirror backend/api/schemas/skills.py exactly.
// ─────────────────────────────────────────

// GET /api/v1/skills/top-growing
export interface GrowingSkill {
  skill_name: string
  skill_category: string
  is_ai_related: boolean
  growth_pct: number | null
  avg_demand_score: number | null
}

// GET /api/v1/skills/ai-skills
export interface AISkill {
  skill_name: string
  skill_category: string
  avg_demand_score: number | null
  avg_growth_pct: number | null
  total_mentions: number | null
}

// GET /api/v1/skills/by-category
export interface SkillCategorySummary {
  skill_category: string
  skill_count: number
  avg_growth_pct: number | null
  ai_skill_count: number
}

// GET /api/v1/skills/demand-trend?skill_name=Python
export interface SkillDemandTrend {
  year: number
  skill_name: string
  avg_demand_score: number | null
  avg_growth_pct: number | null
}

// Aggregate type for the page hook
export interface SkillsData {
  topGrowing: GrowingSkill[]
  aiSkills: AISkill[]
  byCategory: SkillCategorySummary[]
  demandTrend: SkillDemandTrend[]
}