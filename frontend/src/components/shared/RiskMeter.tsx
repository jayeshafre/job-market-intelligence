import clsx from 'clsx'

// ─────────────────────────────────────────
// RiskMeter
// Horizontal score bar 0–1 with colour
// coding. Used in AI Impact pages.
// ─────────────────────────────────────────

interface RiskMeterProps {
  value: number | null   // 0–1 scale
  variant?: 'risk' | 'safe'
  showLabel?: boolean
  size?: 'sm' | 'md'
}

export default function RiskMeter({
  value,
  variant = 'risk',
  showLabel = true,
  size = 'md',
}: RiskMeterProps) {
  if (value === null || value === undefined) {
    return <span className="font-mono text-[11px] text-text-muted">N/A</span>
  }

  const pct = Math.round(value * 100)

  // Colour logic
  const color = variant === 'safe'
    ? pct >= 70 ? '#4ADE80' : pct >= 40 ? '#F97316' : '#F87171'
    : pct >= 70 ? '#F87171' : pct >= 40 ? '#F97316' : '#4ADE80'

  const barH = size === 'sm' ? 'h-1' : 'h-1.5'

  return (
    <div className="flex items-center gap-2 w-full">
      <div className={clsx('flex-1 bg-base-700 rounded-full overflow-hidden', barH)}>
        <div
          className={clsx('h-full rounded-full transition-all duration-500', barH)}
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      {showLabel && (
        <span
          className="font-mono text-[11px] font-medium w-8 text-right flex-shrink-0"
          style={{ color }}
        >
          {pct}%
        </span>
      )}
    </div>
  )
}