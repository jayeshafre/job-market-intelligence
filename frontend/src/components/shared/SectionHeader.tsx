// ─────────────────────────────────────────
// SectionHeader
//
// Consistent heading used above every chart
// or widget panel across all dashboard pages.
// ─────────────────────────────────────────

interface SectionHeaderProps {
  title: string
  subtitle?: string
  badge?: string
  action?: React.ReactNode   // optional right-side slot (e.g. a filter button)
}

export default function SectionHeader({
  title,
  subtitle,
  badge,
  action,
}: SectionHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <div className="flex items-center gap-2">
          <h2 className="text-[14px] font-semibold text-text-primary tracking-tight">
            {title}
          </h2>
          {badge && (
            <span
              className="font-mono text-[9px] uppercase tracking-widest px-1.5 py-0.5 rounded"
              style={{
                background: 'rgba(34,211,238,0.10)',
                border: '1px solid rgba(34,211,238,0.2)',
                color: '#22D3EE',
              }}
            >
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="font-mono text-[11px] text-text-muted mt-0.5">{subtitle}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}