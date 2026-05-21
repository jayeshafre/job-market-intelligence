// ─────────────────────────────────────────
// types/dashboard.ts
//
// AUDIT FIX: Removed all invented types that
// didn't match real backend schemas.
//
// Real per-domain types live in:
//   types/workforce.ts  ← workforce.py schema
//   types/salary.ts     ← salary.py schema
//   types/skills.ts     ← skills.py schema
//   types/aiImpact.ts   ← ai_impact.py schema
//
// This file now only contains:
//   1. The shared FetchStatus/FetchState helpers
//   2. The KpiSummary type — derived client-side
//      from real workforce + salary data since
//      the backend has no /analytics/summary yet.
//   3. The DashboardData aggregate type
// ─────────────────────────────────────────

// Re-export real types used by dashboard widgets
// so existing imports keep working.
export type { CountryHiringStats as CountryStat }   from './workforce'
export type { IndustryHiringStats as IndustryStat } from './workforce'
export type { RemoteBreakdown as RemoteSplit }       from './workforce'
export type { HiringTrendPoint }                     from './workforce'
export type { HiringTrendPoint as HiringTrendData }  from './workforce'

// ── KPI Summary ───────────────────────────
// Derived client-side in analyticsService.ts
// by combining data from:
//   GET /api/v1/workforce/hiring-trends   → total_postings, remote_postings
//   GET /api/v1/workforce/by-country      → total_countries
//   GET /api/v1/workforce/by-industry     → total_industries
//   GET /api/v1/salary/trends             → avg_salary_usd, salary_growth_pct
//   GET /api/v1/ai-impact/trends          → avg_automation_risk
//   GET /api/v1/skills/top-growing        → top skill name

export interface KpiSummary {
  total_job_postings:    number        // from hiring-trends: latest year total_postings
  avg_salary_usd:        number        // from salary/trends: latest avg_salary_usd
  total_countries:       number        // from workforce/by-country: array length
  total_industries:      number        // from workforce/by-industry: array length
  top_growing_skill:     string        // from skills/top-growing: first item skill_name
  ai_disruption_index:   number        // from ai-impact/trends: latest avg_automation_risk
  yoy_job_growth_pct:    number        // computed: (latest - prev) / prev * 100
  yoy_salary_growth_pct: number        // from salary/trends: latest salary_growth_pct
}

// ── Dashboard aggregate ───────────────────
// All data the Main Dashboard page needs

import type { HiringTrendPoint }    from './workforce'
import type { CountryHiringStats }  from './workforce'
import type { IndustryHiringStats } from './workforce'
import type { RemoteBreakdown }     from './workforce'

export interface DashboardData {
  kpi:            KpiSummary
  hiringTrend:    HiringTrendPoint[]      // total_postings + remote_postings per year
  topIndustries:  IndustryHiringStats[]   // real backend fields: total_postings, ai_adoption_index
  topCountries:   CountryHiringStats[]    // real backend fields: total_postings, avg_salary_usd
  remoteSplit:    RemoteBreakdown         // real backend fields: remote_pct, remote_postings, onsite_postings
}

// ── Shared fetch state helpers ────────────

export type FetchStatus = 'idle' | 'loading' | 'success' | 'error'

export interface FetchState<T> {
  data:   T | null
  status: FetchStatus
  error:  string | null
}