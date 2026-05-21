// ─────────────────────────────────────────
// types/workforce.ts
// Field names mirror backend/api/schemas/workforce.py exactly.
// ─────────────────────────────────────────

// GET /api/v1/workforce/hiring-trends
export interface HiringTrendPoint {
  year: number
  total_postings: number
  avg_salary_usd: number | null
  remote_postings: number
}

// GET /api/v1/workforce/by-country
export interface CountryHiringStats {
  country_name: string
  country_code: string
  region: string
  total_postings: number
  avg_salary_usd: number | null
}

// GET /api/v1/workforce/by-industry
export interface IndustryHiringStats {
  industry_name: string
  sector: string
  total_postings: number
  avg_salary_usd: number | null
  ai_adoption_index: number
}

// GET /api/v1/workforce/remote-stats
export interface RemoteBreakdown {
  total_postings: number
  remote_postings: number
  onsite_postings: number
  remote_pct: number
}

// GET /api/v1/workforce/top-roles
export interface TopRole {
  role_name: string
  role_category: string
  seniority_level: string
  total_postings: number
  avg_salary_usd: number | null
  is_remote_eligible: boolean
}

// Aggregate type for the page hook
export interface WorkforceData {
  hiringTrends: HiringTrendPoint[]
  byCountry: CountryHiringStats[]
  byIndustry: IndustryHiringStats[]
  remoteStats: RemoteBreakdown
  topRoles: TopRole[]
}