import api from './api'
import type { KpiSummary, DashboardData } from '@/types/dashboard'
import type { HiringTrendPoint, CountryHiringStats, IndustryHiringStats, RemoteBreakdown } from '@/types/workforce'
import type { SalaryTrendPoint } from '@/types/salary'
import type { GrowingSkill } from '@/types/skills'
import type { DisruptionTrend } from '@/types/aiImpact'

// ─────────────────────────────────────────
// analyticsService.ts
//
// AUDIT FIX: Removed /analytics/summary (doesn't exist).
// AUDIT FIX: All types now use real backend field names.
// AUDIT FIX: KpiSummary is now derived from 5 real endpoints.
// AUDIT FIX: No mock data. If backend is unreachable the
//            error bubbles up to the hook → shown in UI.
//
// Data flow:
//   Backend endpoints → unwrap {success,data} → typed TS → KpiSummary
// ─────────────────────────────────────────

// ── Envelope unwrapper ────────────────────
// Every FastAPI response is: { success, data, message, count }

interface Envelope<T> {
  success: boolean
  data: T
  message: string
  count?: number
}

async function get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
  const res = await api.get<Envelope<T>>(endpoint, { params })
  if (!res.data.success) {
    throw new Error(res.data.message || `API error on ${endpoint}`)
  }
  return res.data.data
}

// ─────────────────────────────────────────
// Individual real endpoint calls
// ─────────────────────────────────────────

async function fetchHiringTrends(): Promise<HiringTrendPoint[]> {
  // GET /api/v1/workforce/hiring-trends?start_year=2018&end_year=2024
  // Returns: { year, total_postings, avg_salary_usd, remote_postings }
  return get<HiringTrendPoint[]>('/workforce/hiring-trends', { start_year: 2018, end_year: 2024 })
}

async function fetchByCountry(): Promise<CountryHiringStats[]> {
  // GET /api/v1/workforce/by-country?year=2024&limit=10
  // Returns: { country_name, country_code, region, total_postings, avg_salary_usd }
  return get<CountryHiringStats[]>('/workforce/by-country', { year: 2024, limit: 10 })
}

async function fetchByIndustry(): Promise<IndustryHiringStats[]> {
  // GET /api/v1/workforce/by-industry?year=2024&limit=10
  // Returns: { industry_name, sector, total_postings, avg_salary_usd, ai_adoption_index }
  return get<IndustryHiringStats[]>('/workforce/by-industry', { year: 2024, limit: 10 })
}

async function fetchRemoteStats(): Promise<RemoteBreakdown> {
  // GET /api/v1/workforce/remote-stats?year=2024
  // Returns: { total_postings, remote_postings, onsite_postings, remote_pct }
  return get<RemoteBreakdown>('/workforce/remote-stats', { year: 2024 })
}

async function fetchSalaryTrends(): Promise<SalaryTrendPoint[]> {
  // GET /api/v1/salary/trends?start_year=2018&end_year=2024
  // Returns: { year, avg_salary_usd, salary_growth_pct, median_salary_usd }
  return get<SalaryTrendPoint[]>('/salary/trends', { start_year: 2018, end_year: 2024 })
}

async function fetchTopGrowingSkill(): Promise<GrowingSkill[]> {
  // GET /api/v1/skills/top-growing?year=2024&limit=1
  // Returns: [{ skill_name, skill_category, is_ai_related, growth_pct, avg_demand_score }]
  return get<GrowingSkill[]>('/skills/top-growing', { year: 2024, limit: 1 })
}

async function fetchDisruptionTrends(): Promise<DisruptionTrend[]> {
  // GET /api/v1/ai-impact/trends?start_year=2024&end_year=2024
  // Returns: [{ year, avg_automation_risk, avg_future_safe, avg_ai_replacement }]
  return get<DisruptionTrend[]>('/ai-impact/trends', { start_year: 2024, end_year: 2024 })
}

// ─────────────────────────────────────────
// deriveKpi
//
// Builds KpiSummary from real API responses.
// No invented numbers. Every field is traceable
// to a specific endpoint + field.
// ─────────────────────────────────────────

function deriveKpi(
  trends:      HiringTrendPoint[],
  countries:   CountryHiringStats[],
  industries:  IndustryHiringStats[],
  salaryPts:   SalaryTrendPoint[],
  topSkills:   GrowingSkill[],
  disruption:  DisruptionTrend[],
): KpiSummary {
  // Latest hiring year
  const sorted      = [...trends].sort((a, b) => b.year - a.year)
  const latest      = sorted[0]
  const previous    = sorted[1]

  const total_job_postings = latest?.total_postings ?? 0

  // YoY job growth %: (latest - previous) / previous * 100
  const yoy_job_growth_pct =
    latest && previous && previous.total_postings > 0
      ? parseFloat((((latest.total_postings - previous.total_postings) / previous.total_postings) * 100).toFixed(1))
      : 0

  // Salary from latest salary trend point
  const latestSalary        = [...salaryPts].sort((a, b) => b.year - a.year)[0]
  const avg_salary_usd      = latestSalary?.avg_salary_usd ?? 0
  const yoy_salary_growth_pct = latestSalary?.salary_growth_pct ?? 0

  // Counts from array lengths
  const total_countries  = countries.length
  const total_industries = industries.length

  // Top skill from skills endpoint
  const top_growing_skill = topSkills[0]?.skill_name ?? 'N/A'

  // Disruption index from latest trend point
  const ai_disruption_index = disruption[0]?.avg_automation_risk ?? 0

  return {
    total_job_postings,
    avg_salary_usd,
    total_countries,
    total_industries,
    top_growing_skill,
    ai_disruption_index,
    yoy_job_growth_pct,
    yoy_salary_growth_pct,
  }
}

// ─────────────────────────────────────────
// fetchDashboardData — main export
//
// Called by useDashboardStats hook.
// Fetches all required data in parallel,
// derives KPI, returns typed DashboardData.
// ─────────────────────────────────────────

export async function fetchDashboardData(): Promise<DashboardData> {
  const [
    hiringTrend,
    topCountries,
    topIndustries,
    remoteSplit,
    salaryTrends,
    topSkills,
    disruptionTrends,
  ] = await Promise.all([
    fetchHiringTrends(),
    fetchByCountry(),
    fetchByIndustry(),
    fetchRemoteStats(),
    fetchSalaryTrends(),
    fetchTopGrowingSkill(),
    fetchDisruptionTrends(),
  ])

  const kpi = deriveKpi(
    hiringTrend,
    topCountries,
    topIndustries,
    salaryTrends,
    topSkills,
    disruptionTrends,
  )

  return {
    kpi,
    hiringTrend,
    topIndustries,
    topCountries,
    remoteSplit,
  }
}