// ─────────────────────────────────────────
// types/salary.ts
// Field names mirror backend/api/schemas/salary.py exactly.
// ─────────────────────────────────────────

// GET /api/v1/salary/by-role
export interface RoleSalary {
  role_name: string
  role_category: string
  seniority_level: string
  avg_salary_usd: number
  data_points: number
}

// GET /api/v1/salary/by-country
export interface CountrySalary {
  country_name: string
  country_code: string
  region: string
  avg_salary_usd: number
  data_points: number
}

// GET /api/v1/salary/trends
export interface SalaryTrendPoint {
  year: number
  avg_salary_usd: number
  salary_growth_pct: number | null    // null for first year (no baseline)
  median_salary_usd: number | null
}

// GET /api/v1/salary/top-paying-roles
export interface TopPayingRole {
  rank: number
  role_name: string
  role_category: string
  seniority_level: string
  avg_salary_usd: number
}

// GET /api/v1/salary/top-paying-countries
export interface TopPayingCountry {
  rank: number
  country_name: string
  country_code: string
  region: string
  avg_salary_usd: number
}

// Aggregate type for the page hook
export interface SalaryData {
  byRole: RoleSalary[]
  byCountry: CountrySalary[]
  trends: SalaryTrendPoint[]
  topRoles: TopPayingRole[]
  topCountries: TopPayingCountry[]
}