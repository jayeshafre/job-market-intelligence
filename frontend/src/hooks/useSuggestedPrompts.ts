import type { ChatIntent } from '@/types/ai'

// ─────────────────────────────────────────
// useSuggestedPrompts
//
// Curated prompts that map to each intent
// in orchestrator.py's INTENT_KEYWORDS.
// Grouped by intent so the UI can show
// contextually relevant suggestions.
// ─────────────────────────────────────────

export interface SuggestedPrompt {
  text:     string
  intent:   ChatIntent
  category: string
}

const ALL_PROMPTS: SuggestedPrompt[] = [
  // salary
  { text: 'Which countries pay the highest salaries for software engineers?', intent: 'salary',        category: 'Salary' },
  { text: 'What is the average salary for a Data Engineer in 2024?',          intent: 'salary',        category: 'Salary' },
  { text: 'How has global average salary grown since 2018?',                  intent: 'salary',        category: 'Salary' },
  { text: 'What salary range can I expect as a senior ML engineer?',          intent: 'salary',        category: 'Salary' },
  // skills
  { text: 'Which skills are growing fastest in 2024?',                        intent: 'skills',        category: 'Skills' },
  { text: 'What AI and ML skills are most in demand right now?',              intent: 'skills',        category: 'Skills' },
  { text: 'Should I learn Kubernetes or Terraform for cloud careers?',        intent: 'skills',        category: 'Skills' },
  { text: 'Which programming languages are employers looking for?',           intent: 'skills',        category: 'Skills' },
  // hiring
  { text: 'Which industries are hiring the most in 2024?',                    intent: 'hiring',        category: 'Hiring' },
  { text: 'What percentage of jobs are now remote?',                          intent: 'hiring',        category: 'Hiring' },
  { text: 'Which countries have the highest job posting volumes?',            intent: 'hiring',        category: 'Hiring' },
  { text: 'What are the top job roles by posting volume globally?',           intent: 'hiring',        category: 'Hiring' },
  // ai disruption
  { text: 'Which jobs are safest from AI automation?',                        intent: 'ai_disruption', category: 'AI Impact' },
  { text: 'What is the automation risk for financial analysts?',              intent: 'ai_disruption', category: 'AI Impact' },
  { text: 'Which industries face the highest AI disruption risk?',            intent: 'ai_disruption', category: 'AI Impact' },
  { text: 'How does AI replacement risk vary by seniority level?',            intent: 'ai_disruption', category: 'AI Impact' },
  // forecast
  { text: 'What are the biggest workforce trends expected in 2025?',          intent: 'forecast',      category: 'Forecast' },
  { text: 'Which skills will be most valuable in the next 3 years?',          intent: 'forecast',      category: 'Forecast' },
  { text: 'How will AI adoption change hiring patterns going forward?',       intent: 'forecast',      category: 'Forecast' },
]

// Default prompts shown on empty chat (mix of intents)
const DEFAULT_PROMPTS: SuggestedPrompt[] = [
  ALL_PROMPTS[4],   // fastest growing skills
  ALL_PROMPTS[12],  // safest from AI
  ALL_PROMPTS[0],   // highest paying countries
  ALL_PROMPTS[8],   // most hiring industries
  ALL_PROMPTS[16],  // workforce trends 2025
  ALL_PROMPTS[6],   // Kubernetes vs Terraform
]

export function useSuggestedPrompts(lastIntent?: ChatIntent) {
  // After a response, suggest follow-up prompts matching the same intent
  const contextual = lastIntent
    ? ALL_PROMPTS.filter(p => p.intent === lastIntent).slice(0, 3)
    : DEFAULT_PROMPTS

  return {
    defaultPrompts:    DEFAULT_PROMPTS,
    contextualPrompts: contextual,
    allPrompts:        ALL_PROMPTS,
  }
}