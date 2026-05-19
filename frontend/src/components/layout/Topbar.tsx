import { useLocation } from 'react-router-dom'
import { useAppMode } from '@/context/AppModeContext'

// ─────────────────────────────────────────
// Path → readable title map
// Add a new entry whenever you add a page
// ─────────────────────────────────────────

const PATH_META: Record<string, { title: string; crumb: string }> = {
  '/dashboard':                    { title: 'Main Dashboard',      crumb: 'overview / main' },
  '/dashboard/live':               { title: 'Live Analytics',      crumb: 'overview / live' },
  '/dashboard/workforce':          { title: 'Workforce Analytics', crumb: 'intelligence / workforce' },
  '/dashboard/salary':             { title: 'Salary Intelligence', crumb: 'intelligence / salary' },
  '/dashboard/skills':             { title: 'Skill Intelligence',  crumb: 'intelligence / skills' },
  '/dashboard/ai-impact':          { title: 'AI Impact Analysis',  crumb: 'intelligence / ai-impact' },
  '/dashboard/forecasting':        { title: 'Forecasting',         crumb: 'predictive / forecasting' },
  '/dashboard/recommendations':    { title: 'Recommendations',     crumb: 'predictive / recommendations' },
  '/dashboard/data-explorer':      { title: 'Data Explorer',       crumb: 'data / explorer' },
  '/dashboard/reports':            { title: 'Reports',             crumb: 'data / reports' },
  '/chat':                         { title: 'AI Assistant',        crumb: 'chatbot / assistant' },
  '/chat/history':                 { title: 'Chat History',        crumb: 'chatbot / history' },
  '/chat/saved':                   { title: 'Saved Prompts',       crumb: 'chatbot / saved' },
  '/chat/settings':                { title: 'Model Settings',      crumb: 'chatbot / settings' },
  '/chat/context':                 { title: 'Data Context',        crumb: 'chatbot / context' },
}

export default function Topbar() {
  const location = useLocation()
  const { isDashboard } = useAppMode()

  const meta = PATH_META[location.pathname] ?? {
    title: 'Page',
    crumb: 'dashboard',
  }

  return (
    <header className="h-[52px] flex items-center px-6 gap-4 bg-base-800 border-b border-border flex-shrink-0">
      {/* Breadcrumb */}
      <span className="font-mono text-[11px] text-text-muted tracking-wide">
        {isDashboard ? 'dashboard' : 'chatbot'} /
      </span>

      {/* Page title */}
      <span className="text-[14px] font-medium text-text-primary">
        {meta.title}
      </span>

      {/* Path detail */}
      <span className="font-mono text-[11px] text-text-muted hidden sm:block">
        {meta.crumb}
      </span>

      {/* Right side — API status */}
      <div className="ml-auto flex items-center gap-2.5">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse-dot" />
          <span className="font-mono text-[11px] text-text-secondary">
            API Connected
          </span>
        </div>
        <span className="font-mono text-[11px] text-text-muted border-l border-border pl-2.5">
          v1.0.0
        </span>
      </div>
    </header>
  )
}