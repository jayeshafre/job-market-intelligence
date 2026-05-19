import type { CountryStat } from '@/types/dashboard'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// TopCountriesWidget
//
// Compact ranked table — top 5 countries.
// Shows: rank, country, job count, avg salary
// Data source: GET /workforce/top-countries
// ─────────────────────────────────────────

interface Props {
  data: CountryStat[]
  isLoading?: boolean
}

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse space-y-3">
      <div className="h-4 w-32 bg-base-600 rounded" />
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-8 bg-base-700 rounded" />
      ))}
    </div>
  )
}

export default function TopCountriesWidget({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  return (
    <div className="kpi-card page-enter h-full">
      <SectionHeader
        title="Top Hiring Countries"
        subtitle="By job volume & avg. salary"
      />

      {/* Table header */}
      <div className="grid grid-cols-12 gap-2 mb-2 px-1">
        <span className="col-span-1 font-mono text-[10px] text-text-muted">#</span>
        <span className="col-span-5 font-mono text-[10px] text-text-muted">Country</span>
        <span className="col-span-3 font-mono text-[10px] text-text-muted text-right">Jobs</span>
        <span className="col-span-3 font-mono text-[10px] text-text-muted text-right">Avg Sal.</span>
      </div>

      <div className="space-y-1">
        {data.map((item, idx) => (
          <div
            key={item.country_name}
            className="grid grid-cols-12 gap-2 items-center px-1 py-2 rounded-md hover:bg-base-700 transition-colors duration-150"
          >
            {/* Rank */}
            <span className="col-span-1 font-mono text-[11px] text-text-muted">
              {idx + 1}
            </span>

            {/* Country */}
            <span className="col-span-5 text-[13px] text-text-primary truncate">
              {item.country_name}
            </span>

            {/* Job count */}
            <span className="col-span-3 font-mono text-[11px] text-text-secondary text-right">
              {item.job_count >= 1_000
                ? `${(item.job_count / 1_000).toFixed(0)}K`
                : item.job_count}
            </span>

            {/* Avg salary */}
            <span className="col-span-3 font-mono text-[11px] text-accent-DEFAULT text-right">
              {item.avg_salary_usd >= 1_000
                ? `$${Math.round(item.avg_salary_usd / 1_000)}K`
                : `$${item.avg_salary_usd}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}