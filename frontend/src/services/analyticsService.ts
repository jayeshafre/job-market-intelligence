import api from './api'
import type {
  KpiSummary,
  HiringTrendData,
  IndustryStat,
  CountryStat,
  RemoteSplit,
  DashboardData,
} from '@/types/dashboard'

// ─────────────────────────────────────────
// analyticsService.ts
//
// Maps to FastAPI routers:
//   /analytics  → backend/api/routers/analytics.py
//   /workforce  → backend/api/routers/workforce.py
//
// Each function has a MOCK FALLBACK so the
// frontend works even when the backend is off.
// Remove mock blocks once your API is ready.
// ─────────────────────────────────────────

// ── Mock data (remove when API is ready) ─

const MOCK_KPI: KpiSummary = {
  total_job_postings: 2_431_800,
  avg_salary_usd: 94_200,
  total_countries: 42,
  total_industries: 18,
  top_growing_skill: 'AI/ML Engineering',
  ai_disruption_index: 0.38,
  yoy_job_growth_pct: 12.3,
  yoy_salary_growth_pct: 5.7,
}

const MOCK_TREND: HiringTrendData = [
  { year: 2019, job_postings: 980_000,   remote_postings: 88_000  },
  { year: 2020, job_postings: 1_050_000, remote_postings: 380_000 },
  { year: 2021, job_postings: 1_420_000, remote_postings: 510_000 },
  { year: 2022, job_postings: 1_780_000, remote_postings: 490_000 },
  { year: 2023, job_postings: 2_100_000, remote_postings: 560_000 },
  { year: 2024, job_postings: 2_431_800, remote_postings: 610_000 },
]

const MOCK_INDUSTRIES: IndustryStat[] = [
  { industry_name: 'Technology',       job_count: 580_000, growth_pct: 18.4 },
  { industry_name: 'Healthcare',       job_count: 420_000, growth_pct: 14.1 },
  { industry_name: 'Finance',          job_count: 310_000, growth_pct: 9.8  },
  { industry_name: 'Education',        job_count: 210_000, growth_pct: 7.2  },
  { industry_name: 'Manufacturing',    job_count: 190_000, growth_pct: 3.1  },
]

const MOCK_COUNTRIES: CountryStat[] = [
  { country_name: 'United States', job_count: 820_000, avg_salary_usd: 118_000 },
  { country_name: 'United Kingdom', job_count: 220_000, avg_salary_usd: 85_000  },
  { country_name: 'India',          job_count: 310_000, avg_salary_usd: 28_000  },
  { country_name: 'Germany',        job_count: 180_000, avg_salary_usd: 92_000  },
  { country_name: 'Canada',         job_count: 140_000, avg_salary_usd: 98_000  },
]

const MOCK_REMOTE: RemoteSplit = {
  remote_pct: 28,
  hybrid_pct: 34,
  onsite_pct: 38,
}

// ─────────────────────────────────────────
// APIResponse envelope from backend:
//   { success: true, data: T, message: string, count: number }
// ─────────────────────────────────────────

interface BackendEnvelope<T> {
  success: boolean
  data: T
  message: string
  count?: number
}

async function tryFetch<T>(endpoint: string, mock: T): Promise<T> {
  try {
    const res = await api.get<BackendEnvelope<T>>(endpoint)
    return res.data.data        // unwrap the envelope
  } catch {
    console.warn(`[analyticsService] Using mock data for: ${endpoint}`)
    return mock
  }
}

// ─────────────────────────────────────────
// Public API functions
// ─────────────────────────────────────────

export async function fetchKpiSummary(): Promise<KpiSummary> {
  return tryFetch('/analytics/summary', MOCK_KPI)
}

export async function fetchHiringTrend(): Promise<HiringTrendData> {
  return tryFetch('/workforce/hiring-trends', MOCK_TREND)
}

export async function fetchTopIndustries(): Promise<IndustryStat[]> {
  return tryFetch('/workforce/by-industry', MOCK_INDUSTRIES)
}

export async function fetchTopCountries(): Promise<CountryStat[]> {
  return tryFetch('/workforce/by-country', MOCK_COUNTRIES)
}

export async function fetchRemoteSplit(): Promise<RemoteSplit> {
  return tryFetch('/workforce/remote-stats', MOCK_REMOTE)
}

// ── Aggregate fetch: loads all dashboard data in parallel ──

export async function fetchDashboardData(): Promise<DashboardData> {
  const [kpi, hiringTrend, topIndustries, topCountries, remoteSplit] =
    await Promise.all([
      fetchKpiSummary(),
      fetchHiringTrend(),
      fetchTopIndustries(),
      fetchTopCountries(),
      fetchRemoteSplit(),
    ])

  return { kpi, hiringTrend, topIndustries, topCountries, remoteSplit }
}