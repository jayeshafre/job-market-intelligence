import type { IndustryHiringStats } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// TopIndustriesWidget
//
// AUDIT FIX: Was typed to IndustryStat (invented type
// with job_count + growth_pct — neither field exists
// in the backend IndustryHiringStats schema).
//
// Now correctly typed to IndustryHiringStats:
//   industry_name    string   ← displayed as label
//   sector           string   ← displayed as sub-label
//   total_postings   number   ← real field for bar width
//   avg_salary_usd   number   ← shown alongside
//   ai_adoption_index number  ← shown as an adoption badge
//
// Data source: GET /api/v1/workforce/by-industry
// ─────────────────────────────────────────

interface Props {
  data: IndustryHiringStats[]
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

function fmtPostings(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

export default function TopIndustriesWidget({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  // Guard: empty data
  if (!data.length) return (
    <div className="kpi-card flex items-center justify-center h-40">
      <span className="font-mono text-[12px] text-text-muted">No industry data available</span>
    </div>
  )

  const max = Math.max(...data.map(d => d.total_postings))

  return (
    <div className="kpi-card page-enter h-full">
      <SectionHeader title="Top Industries" subtitle="By total job postings · 2024" />
      <div className="space-y-4">
        {data.slice(0, 6).map((item, idx) => {
          const barPct = max > 0 ? Math.round((item.total_postings / max) * 100) : 0
          // ai_adoption_index is 0–1, display as adoption level not growth
          const adoptionPct = Math.round((item.ai_adoption_index ?? 0) * 100)

          return (
            <div key={item.industry_name}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-text-muted w-4 text-right flex-shrink-0">
                    {idx + 1}
                  </span>
                  <div>
                    <span className="text-[13px] text-text-primary">{item.industry_name}</span>
                    <span className="font-mono text-[10px] text-text-muted ml-2">{item.sector}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] text-text-secondary">
                    {fmtPostings(item.total_postings)}
                  </span>
                  {/* AUDIT FIX: show real ai_adoption_index, not fabricated growth_pct */}
                  <span className="font-mono text-[10px] text-accent-DEFAULT">
                    AI {adoptionPct}%
                  </span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-base-700 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${barPct}%`,
                    background: idx === 0 ? '#22D3EE' : `rgba(34,211,238,${0.7 - idx * 0.1})`,
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