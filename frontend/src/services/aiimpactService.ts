import api from './api'
import type {
  DisruptionScore,
  FutureSafeCareer,
  IndustryDisruption,
  DisruptionTrend,
  AiImpactData,
} from '@/types/aiImpact'

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

const MOCK_DISRUPTION_SCORES: DisruptionScore[] = [
  { role_name: 'Data Entry Clerk',    role_category: 'Admin',    seniority_level: 'Entry',  avg_automation_risk: 0.91, avg_ai_replacement: 0.88, avg_future_safe: 0.12 },
  { role_name: 'Customer Support',    role_category: 'Support',  seniority_level: 'Entry',  avg_automation_risk: 0.82, avg_ai_replacement: 0.78, avg_future_safe: 0.22 },
  { role_name: 'Financial Analyst',   role_category: 'Finance',  seniority_level: 'Mid',    avg_automation_risk: 0.64, avg_ai_replacement: 0.58, avg_future_safe: 0.42 },
  { role_name: 'Backend Developer',   role_category: 'Software', seniority_level: 'Mid',    avg_automation_risk: 0.44, avg_ai_replacement: 0.38, avg_future_safe: 0.64 },
  { role_name: 'ML Engineer',         role_category: 'AI/ML',    seniority_level: 'Senior', avg_automation_risk: 0.18, avg_ai_replacement: 0.14, avg_future_safe: 0.88 },
  { role_name: 'Cloud Architect',     role_category: 'Cloud',    seniority_level: 'Senior', avg_automation_risk: 0.21, avg_ai_replacement: 0.16, avg_future_safe: 0.84 },
  { role_name: 'Product Manager',     role_category: 'Product',  seniority_level: 'Mid',    avg_automation_risk: 0.28, avg_ai_replacement: 0.22, avg_future_safe: 0.78 },
  { role_name: 'UX Designer',         role_category: 'Design',   seniority_level: 'Mid',    avg_automation_risk: 0.32, avg_ai_replacement: 0.26, avg_future_safe: 0.74 },
]

const MOCK_FUTURE_SAFE: FutureSafeCareer[] = [
  { rank: 1, role_name: 'ML Engineer',         role_category: 'AI/ML',    avg_future_safe_score: 0.92, ai_disruption_risk: 0.14, is_remote_eligible: true  },
  { rank: 2, role_name: 'Cloud Architect',      role_category: 'Cloud',    avg_future_safe_score: 0.88, ai_disruption_risk: 0.18, is_remote_eligible: true  },
  { rank: 3, role_name: 'Cybersecurity Analyst',role_category: 'Security', avg_future_safe_score: 0.84, ai_disruption_risk: 0.22, is_remote_eligible: false },
  { rank: 4, role_name: 'Product Manager',      role_category: 'Product',  avg_future_safe_score: 0.80, ai_disruption_risk: 0.26, is_remote_eligible: true  },
  { rank: 5, role_name: 'DevOps Engineer',      role_category: 'Ops',      avg_future_safe_score: 0.78, ai_disruption_risk: 0.28, is_remote_eligible: true  },
  { rank: 6, role_name: 'Data Engineer',        role_category: 'Data',     avg_future_safe_score: 0.74, ai_disruption_risk: 0.31, is_remote_eligible: true  },
  { rank: 7, role_name: 'UX Designer',          role_category: 'Design',   avg_future_safe_score: 0.72, ai_disruption_risk: 0.34, is_remote_eligible: true  },
  { rank: 8, role_name: 'Solutions Architect',  role_category: 'Cloud',    avg_future_safe_score: 0.70, ai_disruption_risk: 0.36, is_remote_eligible: false },
]

const MOCK_BY_INDUSTRY: IndustryDisruption[] = [
  { industry_name: 'Technology',    sector: 'Tech',       avg_automation_risk: 0.28, avg_future_safe: 0.78, ai_adoption_index: 0.91 },
  { industry_name: 'Finance',       sector: 'Finance',    avg_automation_risk: 0.54, avg_future_safe: 0.52, ai_adoption_index: 0.76 },
  { industry_name: 'Healthcare',    sector: 'Health',     avg_automation_risk: 0.42, avg_future_safe: 0.62, ai_adoption_index: 0.64 },
  { industry_name: 'Manufacturing', sector: 'Industrial', avg_automation_risk: 0.74, avg_future_safe: 0.34, ai_adoption_index: 0.58 },
  { industry_name: 'Retail',        sector: 'Consumer',   avg_automation_risk: 0.68, avg_future_safe: 0.38, ai_adoption_index: 0.51 },
  { industry_name: 'Education',     sector: 'Public',     avg_automation_risk: 0.36, avg_future_safe: 0.68, ai_adoption_index: 0.44 },
  { industry_name: 'Logistics',     sector: 'Industrial', avg_automation_risk: 0.72, avg_future_safe: 0.32, ai_adoption_index: 0.62 },
]

const MOCK_TRENDS: DisruptionTrend[] = [
  { year: 2018, avg_automation_risk: 0.28, avg_future_safe: 0.72, avg_ai_replacement: 0.22 },
  { year: 2019, avg_automation_risk: 0.31, avg_future_safe: 0.70, avg_ai_replacement: 0.25 },
  { year: 2020, avg_automation_risk: 0.34, avg_future_safe: 0.68, avg_ai_replacement: 0.28 },
  { year: 2021, avg_automation_risk: 0.36, avg_future_safe: 0.66, avg_ai_replacement: 0.30 },
  { year: 2022, avg_automation_risk: 0.38, avg_future_safe: 0.64, avg_ai_replacement: 0.33 },
  { year: 2023, avg_automation_risk: 0.40, avg_future_safe: 0.61, avg_ai_replacement: 0.36 },
  { year: 2024, avg_automation_risk: 0.42, avg_future_safe: 0.58, avg_ai_replacement: 0.39 },
]

// ─────────────────────────────────────────
// Public service functions
// ─────────────────────────────────────────

export async function fetchDisruptionScores(
  year = 2024,
  limit = 10
): Promise<DisruptionScore[]> {
  try {
    return await get<DisruptionScore[]>('/ai-impact/disruption-scores', { year, limit })
  } catch {
    console.warn('[aiImpactService] Using mock: disruption-scores')
    return MOCK_DISRUPTION_SCORES
  }
}

export async function fetchFutureSafeCareers(
  year = 2024,
  limit = 8
): Promise<FutureSafeCareer[]> {
  try {
    return await get<FutureSafeCareer[]>('/ai-impact/future-safe-careers', { year, limit })
  } catch {
    console.warn('[aiImpactService] Using mock: future-safe-careers')
    return MOCK_FUTURE_SAFE
  }
}

export async function fetchDisruptionByIndustry(year = 2024): Promise<IndustryDisruption[]> {
  try {
    return await get<IndustryDisruption[]>('/ai-impact/by-industry', { year })
  } catch {
    console.warn('[aiImpactService] Using mock: by-industry')
    return MOCK_BY_INDUSTRY
  }
}

export async function fetchDisruptionTrends(
  startYear = 2018,
  endYear = 2024
): Promise<DisruptionTrend[]> {
  try {
    return await get<DisruptionTrend[]>('/ai-impact/trends', {
      start_year: startYear,
      end_year: endYear,
    })
  } catch {
    console.warn('[aiImpactService] Using mock: trends')
    return MOCK_TRENDS
  }
}

export async function fetchAiImpactData(): Promise<AiImpactData> {
  const [disruptionScores, futureSafeCareers, byIndustry, trends] = await Promise.all([
    fetchDisruptionScores(),
    fetchFutureSafeCareers(),
    fetchDisruptionByIndustry(),
    fetchDisruptionTrends(),
  ])
  return { disruptionScores, futureSafeCareers, byIndustry, trends }
}