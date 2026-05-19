// ─────────────────────────────────────────
// dashboard.ts — Frontend types
//
// These mirror the Pydantic schemas in:
//   backend/api/schemas/analytics.py
//   backend/api/schemas/workforce.py
//   backend/api/schemas/salary.py
// ─────────────────────────────────────────

// ── Generic API wrapper ──────────────────

export interface ApiResponse<T> {
  data: T
  status: 'success' | 'error'
  message?: string
}

// ── KPI Summary (Main Dashboard) ─────────
// Matches: GET /analytics/summary

export interface KpiSummary {
  total_job_postings: number        // e.g. 2_400_000
  avg_salary_usd: number            // e.g. 94000
  total_countries: number           // e.g. 42
  total_industries: number          // e.g. 18
  top_growing_skill: string         // e.g. "AI/ML Engineering"
  ai_disruption_index: number       // e.g. 0.38  (0–1 scale)
  yoy_job_growth_pct: number        // e.g. 12.3
  yoy_salary_growth_pct: number     // e.g. 5.7
}

// ── Hiring Trend (line chart) ─────────────
// Matches: GET /workforce/hiring-trend

export interface HiringTrendPoint {
  year: number                      // e.g. 2020
  job_postings: number              // e.g. 1_200_000
  remote_postings: number           // e.g. 340_000
}

export type HiringTrendData = HiringTrendPoint[]

// ── Top Industries ────────────────────────
// Matches: GET /analytics/top-industries

export interface IndustryStat {
  industry_name: string
  job_count: number
  growth_pct: number
}

// ── Top Countries ─────────────────────────
// Matches: GET /workforce/top-countries

export interface CountryStat {
  country_name: string
  job_count: number
  avg_salary_usd: number
}

// ── Remote Work Split ─────────────────────
// Matches: GET /workforce/remote-split

export interface RemoteSplit {
  remote_pct: number
  hybrid_pct: number
  onsite_pct: number
}

// ── Dashboard page aggregate ──────────────
// All data the Main Dashboard needs

export interface DashboardData {
  kpi: KpiSummary
  hiringTrend: HiringTrendData
  topIndustries: IndustryStat[]
  topCountries: CountryStat[]
  remoteSplit: RemoteSplit
}

// ── Fetch state helper ────────────────────

export type FetchStatus = 'idle' | 'loading' | 'success' | 'error'

export interface FetchState<T> {
  data: T | null
  status: FetchStatus
  error: string | null
}