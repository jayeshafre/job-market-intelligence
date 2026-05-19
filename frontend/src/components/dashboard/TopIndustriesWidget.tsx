import type { IndustryStat } from '@/types/dashboard'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// TopIndustriesWidget
//
// Horizontal bar list — top 5 industries.
// Each bar shows relative share of total jobs.
// Data source: GET /analytics/top-industries
// ─────────────────────────────────────────

interface Props {
  data: IndustryStat[]
  isLoading?: boolean
}

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse space-y-3">
      <div className="h-4 w-36 bg-base-600 rounded" />
      {[...Array(5)].map((_, i) => (
        <div key={i} className="space-y-1.5">
          <div className="h-3 w-28 bg-base-600 rounded" />
          <div className="h-2 rounded-full bg-base-600" style={{ width: `${70 - i * 12}%` }} />
        </div>
      ))}
    </div>
  )
}

export default function TopIndustriesWidget({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  const max = Math.max(...data.map((d) => d.job_count))

  return (
    <div className="kpi-card page-enter h-full">
      <SectionHeader
        title="Top Industries"
        subtitle="By total job postings"
      />

      <div className="space-y-4">
        {data.map((item, idx) => {
          const barPct = Math.round((item.job_count / max) * 100)
          const isPositive = item.growth_pct > 0

          return (
            <div key={item.industry_name}>
              {/* Row label */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span
                    className="font-mono text-[10px] text-text-muted w-4 text-right flex-shrink-0"
                  >
                    {idx + 1}
                  </span>
                  <span className="text-[13px] text-text-primary">
                    {item.industry_name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] text-text-secondary">
                    {item.job_count >= 1_000
                      ? `${(item.job_count / 1_000).toFixed(0)}K`
                      : item.job_count}
                  </span>
                  <span
                    className={`font-mono text-[10px] ${
                      isPositive ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {isPositive ? '+' : ''}{item.growth_pct.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Bar */}
              <div className="h-1.5 rounded-full bg-base-700 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${barPct}%`,
                    background: idx === 0
                      ? '#22D3EE'
                      : `rgba(34,211,238,${0.7 - idx * 0.12})`,
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}