import api from './api'
import type {
  GrowingSkill,
  AISkill,
  SkillCategorySummary,
  SkillDemandTrend,
  SkillsData,
} from '@/types/skills'

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

const MOCK_TOP_GROWING: GrowingSkill[] = [
  { skill_name: 'Prompt Engineering',  skill_category: 'AI/ML',       is_ai_related: true,  growth_pct: 68.4, avg_demand_score: 8.2 },
  { skill_name: 'LLM Fine-tuning',     skill_category: 'AI/ML',       is_ai_related: true,  growth_pct: 62.1, avg_demand_score: 7.8 },
  { skill_name: 'Kubernetes',          skill_category: 'Cloud/DevOps', is_ai_related: false, growth_pct: 44.3, avg_demand_score: 8.6 },
  { skill_name: 'Rust',                skill_category: 'Programming',  is_ai_related: false, growth_pct: 41.8, avg_demand_score: 7.1 },
  { skill_name: 'dbt',                 skill_category: 'Data',         is_ai_related: false, growth_pct: 38.5, avg_demand_score: 7.4 },
  { skill_name: 'Vector Databases',    skill_category: 'AI/ML',        is_ai_related: true,  growth_pct: 37.2, avg_demand_score: 6.9 },
  { skill_name: 'Apache Kafka',        skill_category: 'Data',         is_ai_related: false, growth_pct: 32.4, avg_demand_score: 7.8 },
  { skill_name: 'Terraform',           skill_category: 'Cloud/DevOps', is_ai_related: false, growth_pct: 28.7, avg_demand_score: 8.1 },
  { skill_name: 'PyTorch',             skill_category: 'AI/ML',        is_ai_related: true,  growth_pct: 26.3, avg_demand_score: 7.6 },
  { skill_name: 'TypeScript',          skill_category: 'Programming',  is_ai_related: false, growth_pct: 22.1, avg_demand_score: 8.4 },
]

const MOCK_AI_SKILLS: AISkill[] = [
  { skill_name: 'PyTorch',           skill_category: 'AI/ML', avg_demand_score: 8.8, avg_growth_pct: 26.3, total_mentions: 18400 },
  { skill_name: 'TensorFlow',        skill_category: 'AI/ML', avg_demand_score: 8.4, avg_growth_pct: 14.2, total_mentions: 16200 },
  { skill_name: 'Prompt Engineering',skill_category: 'AI/ML', avg_demand_score: 8.2, avg_growth_pct: 68.4, total_mentions: 12800 },
  { skill_name: 'LangChain',         skill_category: 'AI/ML', avg_demand_score: 7.9, avg_growth_pct: 58.1, total_mentions: 9400  },
  { skill_name: 'Scikit-learn',      skill_category: 'AI/ML', avg_demand_score: 7.7, avg_growth_pct: 8.4,  total_mentions: 14100 },
  { skill_name: 'Hugging Face',      skill_category: 'AI/ML', avg_demand_score: 7.4, avg_growth_pct: 44.2, total_mentions: 8600  },
  { skill_name: 'Vector Databases',  skill_category: 'AI/ML', avg_demand_score: 6.9, avg_growth_pct: 37.2, total_mentions: 6200  },
]

const MOCK_BY_CATEGORY: SkillCategorySummary[] = [
  { skill_category: 'AI/ML',        skill_count: 18, avg_growth_pct: 38.4, ai_skill_count: 18 },
  { skill_category: 'Cloud/DevOps', skill_count: 22, avg_growth_pct: 28.1, ai_skill_count: 2  },
  { skill_category: 'Data',         skill_count: 16, avg_growth_pct: 22.6, ai_skill_count: 4  },
  { skill_category: 'Programming',  skill_count: 24, avg_growth_pct: 18.3, ai_skill_count: 3  },
  { skill_category: 'Security',     skill_count: 12, avg_growth_pct: 14.8, ai_skill_count: 1  },
  { skill_category: 'Databases',    skill_count: 14, avg_growth_pct: 11.2, ai_skill_count: 2  },
]

const MOCK_DEMAND_TREND: SkillDemandTrend[] = [
  { year: 2018, skill_name: 'Python', avg_demand_score: 6.2, avg_growth_pct: null    },
  { year: 2019, skill_name: 'Python', avg_demand_score: 6.8, avg_growth_pct: 9.7     },
  { year: 2020, skill_name: 'Python', avg_demand_score: 7.4, avg_growth_pct: 8.8     },
  { year: 2021, skill_name: 'Python', avg_demand_score: 7.9, avg_growth_pct: 6.8     },
  { year: 2022, skill_name: 'Python', avg_demand_score: 8.3, avg_growth_pct: 5.1     },
  { year: 2023, skill_name: 'Python', avg_demand_score: 8.7, avg_growth_pct: 4.8     },
  { year: 2024, skill_name: 'Python', avg_demand_score: 9.1, avg_growth_pct: 4.6     },
]

// ─────────────────────────────────────────
// Public service functions
// ─────────────────────────────────────────

export async function fetchTopGrowingSkills(
  year = 2024,
  limit = 10,
  aiOnly = false
): Promise<GrowingSkill[]> {
  try {
    return await get<GrowingSkill[]>('/skills/top-growing', {
      year, limit, ai_only: aiOnly,
    })
  } catch {
    console.warn('[skillsService] Using mock: top-growing')
    return MOCK_TOP_GROWING
  }
}

export async function fetchAISkills(
  year = 2024,
  limit = 10
): Promise<AISkill[]> {
  try {
    return await get<AISkill[]>('/skills/ai-skills', { year, limit })
  } catch {
    console.warn('[skillsService] Using mock: ai-skills')
    return MOCK_AI_SKILLS
  }
}

export async function fetchSkillsByCategory(year = 2024): Promise<SkillCategorySummary[]> {
  try {
    return await get<SkillCategorySummary[]>('/skills/by-category', { year })
  } catch {
    console.warn('[skillsService] Using mock: by-category')
    return MOCK_BY_CATEGORY
  }
}

// skill_name is required by this endpoint
export async function fetchSkillDemandTrend(
  skillName = 'Python',
  startYear = 2018,
  endYear = 2024
): Promise<SkillDemandTrend[]> {
  try {
    return await get<SkillDemandTrend[]>('/skills/demand-trend', {
      skill_name: skillName,
      start_year: startYear,
      end_year: endYear,
    })
  } catch {
    console.warn('[skillsService] Using mock: demand-trend')
    return MOCK_DEMAND_TREND
  }
}

export async function fetchSkillsData(): Promise<SkillsData> {
  const [topGrowing, aiSkills, byCategory, demandTrend] = await Promise.all([
    fetchTopGrowingSkills(),
    fetchAISkills(),
    fetchSkillsByCategory(),
    fetchSkillDemandTrend('Python'),
  ])
  return { topGrowing, aiSkills, byCategory, demandTrend }
}