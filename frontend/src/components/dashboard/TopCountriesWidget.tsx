import type { CountryHiringStats } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// TopCountriesWidget
//
// AUDIT FIX: Was typed to CountryStat with
// field "job_count" — doesn't exist in backend.
// Real backend field is "total_postings".
//
// Also used in SalaryIntelligence with job_count: 0
// (hardcoded fake). Now typed to real backend type
// CountryHiringStats so all callers use real data.
//
// Data source: GET /api/v1/workforce/by-country
// Fields: country_name, country_code, region,
//         total_postings, avg_salary_usd
// ─────────────────────────────────────────

interface Props {
  data: CountryHiringStats[]
  isLoading?: boolean
  // Mode controls which column is shown in the right slot
  // 'postings' → shows total_postings (default, workforce page)
  // 'salary'   → shows only avg_salary_usd (salary intelligence page)
  mode?: 'postings' | 'salary'
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

function fmtPostings(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

function fmtSalary(n: number | null): string {
  if (!n) return '—'
  if (n >= 1_000) return `$${Math.round(n / 1_000)}K`
  return `$${n}`
}

export default function TopCountriesWidget({
  data,
  isLoading = false,
  mode = 'postings',
}: Props) {
  if (isLoading) return <Skeleton />

  if (!data.length) return (
    <div className="kpi-card flex items-center justify-center h-40">
      <span className="font-mono text-[12px] text-text-muted">No country data available</span>
    </div>
  )

  return (
    <div className="kpi-card page-enter h-full">
      <SectionHeader
        title={mode === 'salary' ? 'Top Paying Countries' : 'Top Hiring Countries'}
        subtitle={mode === 'salary' ? 'By avg. salary (USD) · 2024' : 'By job volume & avg. salary · 2024'}
      />

      {/* Column headers */}
      <div className="grid grid-cols-12 gap-2 mb-2 px-1">
        <span className="col-span-1 font-mono text-[10px] text-text-muted">#</span>
        <span className="col-span-4 font-mono text-[10px] text-text-muted">Country</span>
        <span className="col-span-3 font-mono text-[10px] text-text-muted">Region</span>
        {mode === 'postings' && (
          <span className="col-span-2 font-mono text-[10px] text-text-muted text-right">Jobs</span>
        )}
        <span className={`font-mono text-[10px] text-text-muted text-right ${mode === 'postings' ? 'col-span-2' : 'col-span-4'}`}>
          Avg Sal.
        </span>
      </div>

      <div className="space-y-1">
        {data.map((item, idx) => (
          <div key={item.country_name}
            className="grid grid-cols-12 gap-2 items-center px-1 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
            <span className="col-span-1 font-mono text-[11px] text-text-muted">{idx + 1}</span>
            <span className="col-span-4 text-[13px] text-text-primary truncate">{item.country_name}</span>
            <span className="col-span-3 font-mono text-[10px] text-text-muted truncate">{item.region}</span>

            {/* AUDIT FIX: use total_postings (real field), not job_count (invented) */}
            {mode === 'postings' && (
              <span className="col-span-2 font-mono text-[11px] text-text-secondary text-right">
                {fmtPostings(item.total_postings)}
              </span>
            )}

            <span className={`font-mono text-[11px] text-accent-DEFAULT text-right ${mode === 'postings' ? 'col-span-2' : 'col-span-4'}`}>
              {fmtSalary(item.avg_salary_usd)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}