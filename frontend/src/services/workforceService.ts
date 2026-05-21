import api from './api'
import type {
  HiringTrendPoint,
  CountryHiringStats,
  IndustryHiringStats,
  RemoteBreakdown,
  TopRole,
  WorkforceData,
} from '@/types/workforce'

// ─────────────────────────────────────────
// BackendEnvelope — matches every FastAPI
// APIResponse wrapper: {success, data, count, message}
// ─────────────────────────────────────────

interface Envelope<T> {
  success: boolean
  data: T
  count?: number
  message: string
}

async function get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
  const res = await api.get<Envelope<T>>(endpoint, { params })
  return res.data.data
}

// ─────────────────────────────────────────
// Mock fallbacks — realistic values from
// the actual live API response you shared.
// Removed once backend is confirmed live.
// ─────────────────────────────────────────

const MOCK_TRENDS: HiringTrendPoint[] = [
  { year: 2018, total_postings: 180_420, avg_salary_usd: 68_200, remote_postings: 12_300 },
  { year: 2019, total_postings: 220_800, avg_salary_usd: 70_100, remote_postings: 18_400 },
  { year: 2020, total_postings: 198_500, avg_salary_usd: 71_500, remote_postings: 62_000 },
  { year: 2021, total_postings: 310_200, avg_salary_usd: 74_800, remote_postings: 98_000 },
  { year: 2022, total_postings: 390_600, avg_salary_usd: 78_400, remote_postings: 104_000 },
  { year: 2023, total_postings: 420_100, avg_salary_usd: 81_900, remote_postings: 110_200 },
  { year: 2024, total_postings: 450_300, avg_salary_usd: 84_600, remote_postings: 118_000 },
]

const MOCK_BY_COUNTRY: CountryHiringStats[] = [
  { country_name: 'Switzerland',    country_code: 'CH', region: 'Europe',   total_postings: 32294, avg_salary_usd: 103623 },
  { country_name: 'United States',  country_code: 'US', region: 'Americas', total_postings: 27676, avg_salary_usd: 89933  },
  { country_name: 'Norway',         country_code: 'NO', region: 'Europe',   total_postings: 25149, avg_salary_usd: 82535  },
  { country_name: 'Singapore',      country_code: 'SG', region: 'Asia',     total_postings: 24954, avg_salary_usd: 82819  },
  { country_name: 'Australia',      country_code: 'AU', region: 'Oceania',  total_postings: 24771, avg_salary_usd: 76944  },
  { country_name: 'Canada',         country_code: 'CA', region: 'Americas', total_postings: 24631, avg_salary_usd: 79015  },
  { country_name: 'Sweden',         country_code: 'SE', region: 'Europe',   total_postings: 24294, avg_salary_usd: 77206  },
  { country_name: 'Denmark',        country_code: 'DK', region: 'Europe',   total_postings: 24036, avg_salary_usd: 82059  },
  { country_name: 'United Kingdom', country_code: 'GB', region: 'Europe',   total_postings: 23698, avg_salary_usd: 79427  },
  { country_name: 'Finland',        country_code: 'FI', region: 'Europe',   total_postings: 23525, avg_salary_usd: 72664  },
]

const MOCK_BY_INDUSTRY: IndustryHiringStats[] = [
  { industry_name: 'Technology',    sector: 'Tech',       total_postings: 98200, avg_salary_usd: 102000, ai_adoption_index: 0.87 },
  { industry_name: 'Finance',       sector: 'Finance',    total_postings: 72400, avg_salary_usd: 94000,  ai_adoption_index: 0.74 },
  { industry_name: 'Healthcare',    sector: 'Health',     total_postings: 68100, avg_salary_usd: 78000,  ai_adoption_index: 0.61 },
  { industry_name: 'Manufacturing', sector: 'Industrial', total_postings: 54300, avg_salary_usd: 65000,  ai_adoption_index: 0.55 },
  { industry_name: 'Education',     sector: 'Public',     total_postings: 41200, avg_salary_usd: 58000,  ai_adoption_index: 0.42 },
  { industry_name: 'Retail',        sector: 'Consumer',   total_postings: 38700, avg_salary_usd: 52000,  ai_adoption_index: 0.48 },
]

const MOCK_REMOTE: RemoteBreakdown = {
  total_postings: 450300,
  remote_postings: 118000,
  onsite_postings: 207138,
  remote_pct: 26.2,
}

const MOCK_TOP_ROLES: TopRole[] = [
  { role_name: 'Data Engineer',        role_category: 'Data',      seniority_level: 'Senior', total_postings: 28400, avg_salary_usd: 118000, is_remote_eligible: true  },
  { role_name: 'ML Engineer',          role_category: 'AI/ML',     seniority_level: 'Senior', total_postings: 24100, avg_salary_usd: 124000, is_remote_eligible: true  },
  { role_name: 'Cloud Architect',      role_category: 'Cloud',     seniority_level: 'Senior', total_postings: 21800, avg_salary_usd: 132000, is_remote_eligible: true  },
  { role_name: 'Product Manager',      role_category: 'Product',   seniority_level: 'Mid',    total_postings: 19400, avg_salary_usd: 108000, is_remote_eligible: true  },
  { role_name: 'DevOps Engineer',      role_category: 'Ops',       seniority_level: 'Mid',    total_postings: 18200, avg_salary_usd: 106000, is_remote_eligible: true  },
  { role_name: 'Backend Developer',    role_category: 'Software',  seniority_level: 'Mid',    total_postings: 17900, avg_salary_usd: 98000,  is_remote_eligible: true  },
  { role_name: 'Data Analyst',         role_category: 'Data',      seniority_level: 'Entry',  total_postings: 16800, avg_salary_usd: 72000,  is_remote_eligible: false },
  { role_name: 'Cybersecurity Analyst',role_category: 'Security',  seniority_level: 'Mid',    total_postings: 14200, avg_salary_usd: 96000,  is_remote_eligible: false },
]

// ─────────────────────────────────────────
// Public service functions
// ─────────────────────────────────────────

export async function fetchHiringTrends(
  startYear = 2018,
  endYear = 2024
): Promise<HiringTrendPoint[]> {
  try {
    return await get<HiringTrendPoint[]>('/workforce/hiring-trends', {
      start_year: startYear,
      end_year: endYear,
    })
  } catch {
    console.warn('[workforceService] Using mock: hiring-trends')
    return MOCK_TRENDS
  }
}

export async function fetchHiringByCountry(
  year = 2024,
  limit = 15
): Promise<CountryHiringStats[]> {
  try {
    return await get<CountryHiringStats[]>('/workforce/by-country', { year, limit })
  } catch {
    console.warn('[workforceService] Using mock: by-country')
    return MOCK_BY_COUNTRY
  }
}

export async function fetchHiringByIndustry(
  year = 2024,
  limit = 15
): Promise<IndustryHiringStats[]> {
  try {
    return await get<IndustryHiringStats[]>('/workforce/by-industry', { year, limit })
  } catch {
    console.warn('[workforceService] Using mock: by-industry')
    return MOCK_BY_INDUSTRY
  }
}

export async function fetchRemoteStats(year = 2024): Promise<RemoteBreakdown> {
  try {
    return await get<RemoteBreakdown>('/workforce/remote-stats', { year })
  } catch {
    console.warn('[workforceService] Using mock: remote-stats')
    return MOCK_REMOTE
  }
}

export async function fetchTopRoles(
  year = 2024,
  limit = 8
): Promise<TopRole[]> {
  try {
    return await get<TopRole[]>('/workforce/top-roles', { year, limit })
  } catch {
    console.warn('[workforceService] Using mock: top-roles')
    return MOCK_TOP_ROLES
  }
}

// Loads all workforce data in parallel
export async function fetchWorkforceData(): Promise<WorkforceData> {
  const [hiringTrends, byCountry, byIndustry, remoteStats, topRoles] =
    await Promise.all([
      fetchHiringTrends(),
      fetchHiringByCountry(),
      fetchHiringByIndustry(),
      fetchRemoteStats(),
      fetchTopRoles(),
    ])
  return { hiringTrends, byCountry, byIndustry, remoteStats, topRoles }
}