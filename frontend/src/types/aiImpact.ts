// ─────────────────────────────────────────
// types/aiImpact.ts
// Field names mirror backend/api/schemas/ai_impact.py exactly.
// ─────────────────────────────────────────

// GET /api/v1/ai-impact/disruption-scores
export interface DisruptionScore {
  role_name: string
  role_category: string
  seniority_level: string
  avg_automation_risk: number | null   // CANONICAL: automation_risk_score
  avg_ai_replacement: number | null    // CANONICAL: ai_replacement_index
  avg_future_safe: number | null       // CANONICAL: future_safe_score
}

// GET /api/v1/ai-impact/future-safe-careers
export interface FutureSafeCareer {
  rank: number
  role_name: string
  role_category: string
  avg_future_safe_score: number | null  // higher = safer
  ai_disruption_risk: number            // role-level baseline from dim_job_role
  is_remote_eligible: boolean
}

// GET /api/v1/ai-impact/by-industry
export interface IndustryDisruption {
  industry_name: string
  sector: string
  avg_automation_risk: number | null
  avg_future_safe: number | null
  ai_adoption_index: number             // from dim_industry
}

// GET /api/v1/ai-impact/trends
export interface DisruptionTrend {
  year: number
  avg_automation_risk: number | null
  avg_future_safe: number | null
  avg_ai_replacement: number | null
}

// Aggregate type for the page hook
export interface AiImpactData {
  disruptionScores: DisruptionScore[]
  futureSafeCareers: FutureSafeCareer[]
  byIndustry: IndustryDisruption[]
  trends: DisruptionTrend[]
}