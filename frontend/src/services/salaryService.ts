import api from './api'
import type {
  RoleSalary,
  CountrySalary,
  SalaryTrendPoint,
  TopPayingRole,
  TopPayingCountry,
  SalaryData,
} from '@/types/salary'

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

// ── Mocks ─────────────────────────────────

const MOCK_BY_ROLE: RoleSalary[] = [
  { role_name: 'Chief Technology Officer', role_category: 'Executive',  seniority_level: 'C-Suite', avg_salary_usd: 198000, data_points: 120 },
  { role_name: 'ML Engineer',              role_category: 'AI/ML',      seniority_level: 'Senior',  avg_salary_usd: 154000, data_points: 340 },
  { role_name: 'Cloud Architect',          role_category: 'Cloud',      seniority_level: 'Senior',  avg_salary_usd: 148000, data_points: 280 },
  { role_name: 'Data Engineer',            role_category: 'Data',       seniority_level: 'Senior',  avg_salary_usd: 138000, data_points: 410 },
  { role_name: 'DevOps Engineer',          role_category: 'Ops',        seniority_level: 'Mid',     avg_salary_usd: 118000, data_points: 390 },
  { role_name: 'Product Manager',          role_category: 'Product',    seniority_level: 'Mid',     avg_salary_usd: 112000, data_points: 360 },
  { role_name: 'Backend Developer',        role_category: 'Software',   seniority_level: 'Mid',     avg_salary_usd: 104000, data_points: 520 },
  { role_name: 'Data Analyst',             role_category: 'Data',       seniority_level: 'Entry',   avg_salary_usd: 78000,  data_points: 480 },
]

const MOCK_BY_COUNTRY: CountrySalary[] = [
  { country_name: 'Switzerland',   country_code: 'CH', region: 'Europe',   avg_salary_usd: 103623, data_points: 420 },
  { country_name: 'United States', country_code: 'US', region: 'Americas', avg_salary_usd: 89933,  data_points: 980 },
  { country_name: 'Singapore',     country_code: 'SG', region: 'Asia',     avg_salary_usd: 82819,  data_points: 310 },
  { country_name: 'Norway',        country_code: 'NO', region: 'Europe',   avg_salary_usd: 82535,  data_points: 290 },
  { country_name: 'Denmark',       country_code: 'DK', region: 'Europe',   avg_salary_usd: 82059,  data_points: 270 },
  { country_name: 'Australia',     country_code: 'AU', region: 'Oceania',  avg_salary_usd: 76944,  data_points: 350 },
  { country_name: 'Canada',        country_code: 'CA', region: 'Americas', avg_salary_usd: 79015,  data_points: 380 },
  { country_name: 'Germany',       country_code: 'DE', region: 'Europe',   avg_salary_usd: 71872,  data_points: 430 },
]

const MOCK_TRENDS: SalaryTrendPoint[] = [
  { year: 2018, avg_salary_usd: 68200, salary_growth_pct: null,  median_salary_usd: 62000 },
  { year: 2019, avg_salary_usd: 70100, salary_growth_pct: 2.8,   median_salary_usd: 64000 },
  { year: 2020, avg_salary_usd: 71500, salary_growth_pct: 2.0,   median_salary_usd: 65500 },
  { year: 2021, avg_salary_usd: 74800, salary_growth_pct: 4.6,   median_salary_usd: 68000 },
  { year: 2022, avg_salary_usd: 78400, salary_growth_pct: 4.8,   median_salary_usd: 72000 },
  { year: 2023, avg_salary_usd: 81900, salary_growth_pct: 4.5,   median_salary_usd: 75500 },
  { year: 2024, avg_salary_usd: 84600, salary_growth_pct: 3.3,   median_salary_usd: 78000 },
]

const MOCK_TOP_ROLES: TopPayingRole[] = [
  { rank: 1, role_name: 'Chief Technology Officer', role_category: 'Executive', seniority_level: 'C-Suite', avg_salary_usd: 198000 },
  { rank: 2, role_name: 'ML Engineer',              role_category: 'AI/ML',     seniority_level: 'Senior',  avg_salary_usd: 154000 },
  { rank: 3, role_name: 'Cloud Architect',          role_category: 'Cloud',     seniority_level: 'Senior',  avg_salary_usd: 148000 },
  { rank: 4, role_name: 'Data Engineer',            role_category: 'Data',      seniority_level: 'Senior',  avg_salary_usd: 138000 },
  { rank: 5, role_name: 'Cybersecurity Director',   role_category: 'Security',  seniority_level: 'Director',avg_salary_usd: 134000 },
]

const MOCK_TOP_COUNTRIES: TopPayingCountry[] = [
  { rank: 1, country_name: 'Switzerland',   country_code: 'CH', region: 'Europe',   avg_salary_usd: 103623 },
  { rank: 2, country_name: 'United States', country_code: 'US', region: 'Americas', avg_salary_usd: 89933  },
  { rank: 3, country_name: 'Singapore',     country_code: 'SG', region: 'Asia',     avg_salary_usd: 82819  },
  { rank: 4, country_name: 'Norway',        country_code: 'NO', region: 'Europe',   avg_salary_usd: 82535  },
  { rank: 5, country_name: 'Denmark',       country_code: 'DK', region: 'Europe',   avg_salary_usd: 82059  },
]

// ─────────────────────────────────────────
// Public service functions
// ─────────────────────────────────────────

export async function fetchSalaryByRole(
  year = 2024,
  limit = 10
): Promise<RoleSalary[]> {
  try {
    return await get<RoleSalary[]>('/salary/by-role', { year, limit })
  } catch {
    console.warn('[salaryService] Using mock: by-role')
    return MOCK_BY_ROLE
  }
}

export async function fetchSalaryByCountry(
  year = 2024,
  limit = 10
): Promise<CountrySalary[]> {
  try {
    return await get<CountrySalary[]>('/salary/by-country', { year, limit })
  } catch {
    console.warn('[salaryService] Using mock: by-country')
    return MOCK_BY_COUNTRY
  }
}

export async function fetchSalaryTrends(
  startYear = 2018,
  endYear = 2024
): Promise<SalaryTrendPoint[]> {
  try {
    return await get<SalaryTrendPoint[]>('/salary/trends', {
      start_year: startYear,
      end_year: endYear,
    })
  } catch {
    console.warn('[salaryService] Using mock: trends')
    return MOCK_TRENDS
  }
}

export async function fetchTopPayingRoles(
  year = 2024,
  limit = 5
): Promise<TopPayingRole[]> {
  try {
    return await get<TopPayingRole[]>('/salary/top-paying-roles', { year, limit })
  } catch {
    console.warn('[salaryService] Using mock: top-paying-roles')
    return MOCK_TOP_ROLES
  }
}

export async function fetchTopPayingCountries(
  year = 2024,
  limit = 5
): Promise<TopPayingCountry[]> {
  try {
    return await get<TopPayingCountry[]>('/salary/top-paying-countries', { year, limit })
  } catch {
    console.warn('[salaryService] Using mock: top-paying-countries')
    return MOCK_TOP_COUNTRIES
  }
}

export async function fetchSalaryData(): Promise<SalaryData> {
  const [byRole, byCountry, trends, topRoles, topCountries] = await Promise.all([
    fetchSalaryByRole(),
    fetchSalaryByCountry(),
    fetchSalaryTrends(),
    fetchTopPayingRoles(),
    fetchTopPayingCountries(),
  ])
  return { byRole, byCountry, trends, topRoles, topCountries }
}