import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import clsx from 'clsx'

// ─────────────────────────────────────────
// KpiCard
//
// Reusable KPI metric card.
// Used on: Main Dashboard, Live Analytics,
//          Workforce, Salary, AI Impact pages.
//
// Props:
//   label      — short descriptor (e.g. "Total Jobs")
//   value      — formatted string (e.g. "2.4M")
//   delta      — change text (e.g. "+12.3% YoY")
//   trend      — 'up' | 'down' | 'neutral'
//   icon       — lucide React component
//   isLoading  — shows skeleton when true
// ─────────────────────────────────────────

interface KpiCardProps {
  label: string
  value: string
  delta?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ElementType
  accentColor?: string   // optional override, default cyan
  isLoading?: boolean
}

// Format helpers — call these before passing `value`
export function fmtNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}
export function fmtUSD(n: number): string {
  if (n >= 1_000) return `$${Math.round(n / 1_000)}K`
  return `$${n}`
}
export function fmtPct(n: number, decimals = 1): string {
  return `${n.toFixed(decimals)}%`
}

// ── Skeleton loader ───────────────────────

function KpiSkeleton() {
  return (
    <div className="kpi-card animate-pulse">
      <div className="h-3 w-20 bg-base-600 rounded mb-4" />
      <div className="h-7 w-28 bg-base-600 rounded mb-2" />
      <div className="h-3 w-16 bg-base-600 rounded" />
    </div>
  )
}

// ── Main component ────────────────────────

export default function KpiCard({
  label,
  value,
  delta,
  trend = 'neutral',
  icon: Icon,
  isLoading = false,
}: KpiCardProps) {
  if (isLoading) return <KpiSkeleton />

  const trendColor = {
    up:      'text-success',
    down:    'text-danger',
    neutral: 'text-text-muted',
  }[trend]

  const TrendIcon = {
    up:      TrendingUp,
    down:    TrendingDown,
    neutral: Minus,
  }[trend]

  return (
    <div className="kpi-card group page-enter">
      {/* Label row */}
      <div className="flex items-center justify-between mb-3">
        <span className="kpi-label">{label}</span>
        {Icon && (
          <div
            className="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0"
            style={{
              background: 'rgba(34,211,238,0.08)',
              border: '1px solid rgba(34,211,238,0.18)',
            }}
          >
            <Icon size={14} className="text-accent-DEFAULT" aria-hidden="true" />
          </div>
        )}
      </div>

      {/* Value */}
      <p className="kpi-value">{value}</p>

      {/* Delta */}
      {delta && (
        <div className={clsx('flex items-center gap-1 mt-1.5', trendColor)}>
          <TrendIcon size={12} aria-hidden="true" />
          <span className="font-mono text-[11px]">{delta}</span>
        </div>
      )}
    </div>
  )
}