import { useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Activity, Users, Coins, Brain, Bot,
  TrendingUp, Sparkles, Table, FileBarChart,
  MessageSquareText, History, Bookmark, Settings2, Database,
  Globe, ArrowLeftRight,
} from 'lucide-react'
import clsx from 'clsx'
import { useAppMode } from '@/context/AppModeContext'
import { DASHBOARD_NAV, CHATBOT_NAV } from '@/config/navigation'
import type { NavItem, ChatNavItem } from '@/types/navigation'

// ─────────────────────────────────────────
// Icon map — maps string names from config
// to actual Lucide components
// ─────────────────────────────────────────

const ICON_MAP: Record<string, React.ElementType> = {
  LayoutDashboard, Activity, Users, Coins, Brain, Bot,
  TrendingUp, Sparkles, Table, FileBarChart,
  MessageSquareText, History, Bookmark, Settings2, Database,
}

function NavIcon({ name, className }: { name: string; className?: string }) {
  const Icon = ICON_MAP[name]
  if (!Icon) return null
  return <Icon size={16} className={className} aria-hidden="true" />
}

// ─────────────────────────────────────────
// Badge component (LIVE / NEW / BETA)
// ─────────────────────────────────────────

function NavBadge({ text, variant }: { text: string; variant: string }) {
  const isLive = variant === 'live'
  return (
    <span
      className={clsx(
        'ml-auto font-mono text-[10px] font-medium px-1.5 py-0.5 rounded',
        isLive
          ? 'bg-success/10 text-success animate-pulse-dot'
          : 'bg-accent-dim text-accent-DEFAULT border border-accent-border'
      )}
    >
      {text}
    </span>
  )
}

// ─────────────────────────────────────────
// Single nav item — dashboard pages
// ─────────────────────────────────────────

function DashNavItem({ item }: { item: NavItem }) {
  const location = useLocation()
  const navigate = useNavigate()
  const isActive = location.pathname === item.path ||
    (item.path !== '/dashboard' && location.pathname.startsWith(item.path))

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => navigate(item.path)}
      onKeyDown={(e) => e.key === 'Enter' && navigate(item.path)}
      className={clsx('nav-item', isActive && 'active')}
      aria-current={isActive ? 'page' : undefined}
    >
      <NavIcon
        name={item.icon}
        className={clsx(
          'nav-icon flex-shrink-0',
          isActive ? 'text-accent-DEFAULT' : 'text-text-secondary'
        )}
      />
      <span className={clsx('nav-label', isActive ? 'text-accent-DEFAULT' : 'text-text-secondary')}>
        {item.label}
      </span>
      {item.badge && <NavBadge text={item.badge.text} variant={item.badge.variant} />}
    </div>
  )
}

// ─────────────────────────────────────────
// Single nav item — chatbot pages
// ─────────────────────────────────────────

function ChatNavItem({ item }: { item: ChatNavItem }) {
  const location = useLocation()
  const navigate = useNavigate()
  const isActive = location.pathname === item.path ||
    (item.path !== '/chat' && location.pathname.startsWith(item.path))

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => navigate(item.path)}
      onKeyDown={(e) => e.key === 'Enter' && navigate(item.path)}
      className={clsx('nav-item', isActive && 'active')}
      aria-current={isActive ? 'page' : undefined}
    >
      <NavIcon
        name={item.icon}
        className={clsx(
          'nav-icon flex-shrink-0',
          isActive ? 'text-accent-DEFAULT' : 'text-text-secondary'
        )}
      />
      <span className={clsx('nav-label', isActive ? 'text-accent-DEFAULT' : 'text-text-secondary')}>
        {item.label}
      </span>
    </div>
  )
}

// ─────────────────────────────────────────
// Mode toggle button — bottom of sidebar
// ─────────────────────────────────────────

function ModeToggleButton() {
  const { mode, toggleMode, isDashboard } = useAppMode()
  const navigate = useNavigate()

  function handleToggle() {
    toggleMode()
    // Navigate to the root of the target mode
    navigate(isDashboard ? '/chat' : '/dashboard')
  }

  return (
    <button
      onClick={handleToggle}
      aria-label={`Switch to ${isDashboard ? 'AI Chatbot' : 'Dashboard'}`}
      className="w-full group"
    >
      <div
        className={clsx(
          'flex items-center gap-2.5 p-2.5 rounded-xl',
          'bg-base-700 border border-border',
          'transition-all duration-200',
          'group-hover:border-accent-border group-hover:bg-base-600'
        )}
      >
        {/* Icon wrap */}
        <div
          className={clsx(
            'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors duration-200',
            isDashboard
              ? 'bg-cyan-500/10'
              : 'bg-indigo-500/10'
          )}
        >
          {isDashboard ? (
            <MessageSquareText
              size={16}
              className="text-accent-DEFAULT"
              aria-hidden="true"
            />
          ) : (
            <LayoutDashboard
              size={16}
              className="text-info"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Text */}
        <div className="flex-1 text-left min-w-0">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted leading-none">
            Switch to
          </p>
          <p className="text-[13px] font-medium text-text-primary mt-0.5 leading-none">
            {isDashboard ? 'AI Chatbot' : 'Dashboard'}
          </p>
        </div>

        {/* Arrow icon */}
        <ArrowLeftRight
          size={14}
          className="text-text-muted flex-shrink-0 transition-colors duration-150 group-hover:text-text-secondary"
          aria-hidden="true"
        />
      </div>
    </button>
  )
}

// ─────────────────────────────────────────
// Main Sidebar component
// ─────────────────────────────────────────

export default function Sidebar() {
  const { mode, isDashboard } = useAppMode()

  return (
    <aside
      className={clsx(
        'w-[260px] min-h-screen flex flex-col flex-shrink-0',
        'bg-base-800 border-r border-border'
      )}
      aria-label="Main navigation"
    >
      {/* ── Brand header ── */}
      <div className="px-[18px] py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          {/* Brand icon */}
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: 'rgba(34,211,238,0.10)',
              border: '1px solid rgba(34,211,238,0.25)',
            }}
          >
            <Globe size={16} className="text-accent-DEFAULT" aria-hidden="true" />
          </div>

          {/* Brand text */}
          <div>
            <p className="text-[13px] font-semibold text-text-primary leading-tight tracking-[0.01em]">
              JobMarket IQ
            </p>
            <p className="font-mono text-[10px] uppercase tracking-[0.05em] text-text-muted mt-0.5">
              Intelligence Platform
            </p>
          </div>
        </div>
      </div>

      {/* ── Mode badge ── */}
      <div className="mode-badge">
        <div className="mode-badge-dot" />
        <span className="mode-badge-text">
          {isDashboard ? 'Dashboard Mode' : 'Chatbot Mode'}
        </span>
      </div>

      {/* ── Navigation area ── */}
      <nav className="flex-1 overflow-y-auto py-2" aria-label={mode === 'dashboard' ? 'Dashboard pages' : 'Chatbot pages'}>

        {/* Dashboard nav */}
        {isDashboard && (
          <div className="animate-slide-in-left">
            {DASHBOARD_NAV.map((section) => (
              <div key={section.label} className="px-2.5 mt-3 mb-1">
                <p className="nav-section-label">{section.label}</p>
                <div className="flex flex-col gap-0.5 mt-1">
                  {section.items.map((item) => (
                    <DashNavItem key={item.id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Chatbot nav */}
        {!isDashboard && (
          <div className="animate-slide-in-left">
            {CHATBOT_NAV.map((section) => (
              <div key={section.label} className="px-2.5 mt-3 mb-1">
                <p className="nav-section-label">{section.label}</p>
                <div className="flex flex-col gap-0.5 mt-1">
                  {section.items.map((item) => (
                    <ChatNavItem key={item.id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </nav>

      {/* ── Footer: mode toggle ── */}
      <div className="p-2.5 border-t border-border">
        <ModeToggleButton />
      </div>
    </aside>
  )
}