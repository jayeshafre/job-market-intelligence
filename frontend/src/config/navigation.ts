import type { NavSection, ChatNavSection } from '@/types/navigation'

// ─────────────────────────────────────────
// Dashboard navigation structure
// Maps 1:1 to backend router modules:
//   workforce.py / salary.py / skills.py /
//   ai_impact.py / forecast.py / analytics.py
// ─────────────────────────────────────────

export const DASHBOARD_NAV: NavSection[] = [
  {
    label: 'Overview',
    items: [
      {
        id: 'main',
        label: 'Main Dashboard',
        icon: 'LayoutDashboard',
        path: '/dashboard',
      },
      {
        id: 'live',
        label: 'Live Analytics',
        icon: 'Activity',
        path: '/dashboard/live',
        badge: { text: 'LIVE', variant: 'live' },
      },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      {
        id: 'workforce',
        label: 'Workforce Analytics',
        icon: 'Users',
        path: '/dashboard/workforce',
      },
      {
        id: 'salary',
        label: 'Salary Intelligence',
        icon: 'Coins',
        path: '/dashboard/salary',
      },
      {
        id: 'skills',
        label: 'Skill Intelligence',
        icon: 'Brain',
        path: '/dashboard/skills',
        badge: { text: 'NEW', variant: 'new' },
      },
      {
        id: 'ai-impact',
        label: 'AI Impact Analysis',
        icon: 'Bot',
        path: '/dashboard/ai-impact',
      },
    ],
  },
  {
    label: 'Predictive',
    items: [
      {
        id: 'forecasting',
        label: 'Forecasting',
        icon: 'TrendingUp',
        path: '/dashboard/forecasting',
      },
      {
        id: 'recommendations',
        label: 'Recommendations',
        icon: 'Sparkles',
        path: '/dashboard/recommendations',
      },
    ],
  },
  {
    label: 'Data',
    items: [
      {
        id: 'data-explorer',
        label: 'Data Explorer',
        icon: 'Table',
        path: '/dashboard/data-explorer',
      },
      {
        id: 'reports',
        label: 'Reports',
        icon: 'FileBarChart',
        path: '/dashboard/reports',
      },
    ],
  },
]

// ─────────────────────────────────────────
// Chatbot navigation structure
// (Fully wired in Phase 4 — AI chatbot phase)
// ─────────────────────────────────────────

export const CHATBOT_NAV: ChatNavSection[] = [
  {
    label: 'Chatbot',
    items: [
      {
        id: 'assistant',
        label: 'AI Assistant',
        icon: 'MessageSquareText',
        path: '/chat',
      },
      {
        id: 'history',
        label: 'Chat History',
        icon: 'History',
        path: '/chat/history',
      },
      {
        id: 'saved-prompts',
        label: 'Saved Prompts',
        icon: 'Bookmark',
        path: '/chat/saved',
      },
    ],
  },
  {
    label: 'AI Config',
    items: [
      {
        id: 'model-settings',
        label: 'Model Settings',
        icon: 'Settings2',
        path: '/chat/settings',
      },
      {
        id: 'data-context',
        label: 'Data Context',
        icon: 'Database',
        path: '/chat/context',
      },
    ],
  },
]