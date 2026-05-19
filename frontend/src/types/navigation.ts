// ─────────────────────────────────────────
// App mode: the two root "systems" of the platform
// ─────────────────────────────────────────

export type AppMode = 'dashboard' | 'chatbot'

// ─────────────────────────────────────────
// Dashboard pages / nav items
// ─────────────────────────────────────────

export type DashboardPageId =
  | 'main'
  | 'live'
  | 'workforce'
  | 'salary'
  | 'skills'
  | 'ai-impact'
  | 'forecasting'
  | 'recommendations'
  | 'data-explorer'
  | 'reports'

export interface NavItem {
  id: DashboardPageId
  label: string
  icon: string          // lucide-react icon name
  path: string          // react-router path
  badge?: NavBadge
}

export interface NavBadge {
  text: string
  variant: 'live' | 'new' | 'beta'
}

export interface NavSection {
  label: string
  items: NavItem[]
}

// ─────────────────────────────────────────
// Chatbot pages / nav items
// ─────────────────────────────────────────

export type ChatPageId =
  | 'assistant'
  | 'history'
  | 'saved-prompts'
  | 'model-settings'
  | 'data-context'

export interface ChatNavItem {
  id: ChatPageId
  label: string
  icon: string
  path: string
}

export interface ChatNavSection {
  label: string
  items: ChatNavItem[]
}