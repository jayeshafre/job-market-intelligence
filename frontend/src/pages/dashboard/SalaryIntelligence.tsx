import { DollarSign, TrendingUp, Globe, Award } from 'lucide-react'
import { useSalary } from '@/hooks/useSalary'
import PageHeader from '@/components/shared/PageHeader'
import KpiCard, { fmtUSD, fmtPct } from '@/components/dashboard/KpiCard'
import SalaryTrendChart from '@/components/salary/SalaryTrendChart'
import TopPayingRolesChart from '@/components/salary/TopPayingRolesChart'
import TopCountriesWidget from '@/components/dashboard/TopCountriesWidget'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// SalaryIntelligence — fully connected to live API
//
// AUDIT FIX: Was passing { country_name, job_count: 0, avg_salary_usd }
// to TopCountriesWidget — job_count: 0 was hardcoded fake data.
//
// Fix: useSalary now fetches /salary/by-country which returns
// CountrySalary (country_name, country_code, region, avg_salary_usd, data_points).
// BUT TopCountriesWidget expects CountryHiringStats (from workforce router).
//
// Resolution: SalaryIntelligence uses its own inline country table
// built from CountrySalary data, rather than forcing CountrySalary
// into a widget typed for CountryHiringStats.
// TopCountriesWidget is removed from this page entirely.
// ─────────────────────────────────────────

export default function SalaryIntelligence() {
  const { data, status, error, refetch } = useSalary()
  const isLoading = status === 'idle' || status === 'loading'

  const latestTrend  = data?.trends[data.trends.length - 1]
  const avgSalary    = latestTrend?.avg_salary_usd ?? null
  const salaryGrowth = latestTrend?.salary_growth_pct ?? null
  const topRole      = data?.topRoles[0]
  const topCountry   = data?.topCountries[0]

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="intelligence"
        title="Salary Intelligence"
        description="Global salary benchmarks, trends, top-paying roles and countries"
        isLoading={isLoading}
        onRefetch={refetch}
      />

      {error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-danger"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)' }}>
          <span>⚠</span><span>Could not reach backend: {error}</span>
        </div>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Global Avg Salary"
          value={avgSalary && !isLoading ? fmtUSD(avgSalary) : '—'}
          delta={salaryGrowth ? `+${fmtPct(salaryGrowth)} YoY` : undefined}
          trend="up"
          icon={DollarSign}
          isLoading={isLoading}
        />
        <KpiCard
          label="Salary Growth"
          value={salaryGrowth && !isLoading ? `+${fmtPct(salaryGrowth)}` : '—'}
          delta="year-over-year · 2024"
          trend="up"
          icon={TrendingUp}
          isLoading={isLoading}
        />
        <KpiCard
          label="Highest Paid Role"
          value={topRole && !isLoading ? topRole.role_name : '—'}
          delta={topRole ? fmtUSD(topRole.avg_salary_usd) : undefined}
          trend="up"
          icon={Award}
          isLoading={isLoading}
        />
        <KpiCard
          label="Top Paying Country"
          value={topCountry && !isLoading ? topCountry.country_name : '—'}
          delta={topCountry ? fmtUSD(topCountry.avg_salary_usd) : undefined}
          trend="up"
          icon={Globe}
          isLoading={isLoading}
        />
      </div>

      {/* Trend chart + top paying roles chart */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <SalaryTrendChart data={data?.trends ?? []} isLoading={isLoading} />
        <TopPayingRolesChart data={data?.topRoles ?? []} isLoading={isLoading} />
      </div>

      {/* Salary by role table */}
      <div className="kpi-card page-enter">
        <SectionHeader title="Salary by Role" subtitle="Avg salary by job role & seniority · 2024" />
        <div className="grid grid-cols-12 gap-2 px-2 mb-1">
          {['Role', 'Category', 'Level', 'Avg Salary', 'Data Pts'].map((h, i) => (
            <span key={h} className={`font-mono text-[10px] text-text-muted uppercase tracking-wider
              ${i === 0 ? 'col-span-4' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-2' : i === 3 ? 'col-span-2 text-right' : 'col-span-1 text-right'}`}>
              {h}
            </span>
          ))}
        </div>
        <div className="space-y-0.5">
          {(isLoading ? Array(6).fill(null) : (data?.byRole ?? []).slice(0, 8)).map((r, i) =>
            isLoading ? (
              <div key={i} className="h-9 bg-base-700 rounded-lg animate-pulse" />
            ) : (
              <div key={r.role_name}
                className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                <span className="col-span-4 text-[12px] text-text-primary truncate">{r.role_name}</span>
                <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{r.role_category}</span>
                <span className="col-span-2 font-mono text-[10px] text-text-muted">{r.seniority_level}</span>
                <span className="col-span-2 font-mono text-[12px] text-accent-DEFAULT text-right font-medium">
                  {fmtUSD(r.avg_salary_usd)}
                </span>
                <span className="col-span-1 font-mono text-[10px] text-text-muted text-right">
                  {r.data_points}
                </span>
              </div>
            )
          )}
        </div>
      </div>

      {/* Top paying countries — using CountrySalary fields directly */}
      <div className="kpi-card page-enter">
        <SectionHeader title="Top Paying Countries" subtitle="Avg salary (USD) by country · 2024" />
        <div className="grid grid-cols-12 gap-2 px-2 mb-1">
          {['#', 'Country', 'Region', 'Avg Salary', 'Data Pts'].map((h, i) => (
            <span key={h} className={`font-mono text-[10px] text-text-muted uppercase tracking-wider
              ${i === 0 ? 'col-span-1' : i === 1 ? 'col-span-4' : i === 2 ? 'col-span-3' : i === 3 ? 'col-span-3 text-right' : 'col-span-1 text-right'}`}>
              {h}
            </span>
          ))}
        </div>
        <div className="space-y-0.5">
          {(isLoading ? Array(5).fill(null) : (data?.topCountries ?? [])).map((c, i) =>
            isLoading ? (
              <div key={i} className="h-9 bg-base-700 rounded-lg animate-pulse" />
            ) : (
              <div key={c.country_name}
                className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                <span className="col-span-1 font-mono text-[11px] text-text-muted">{c.rank}</span>
                <span className="col-span-4 text-[12px] text-text-primary truncate">{c.country_name}</span>
                <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{c.region}</span>
                <span className="col-span-3 font-mono text-[12px] text-accent-DEFAULT text-right font-medium">
                  {fmtUSD(c.avg_salary_usd)}
                </span>
                <span className="col-span-1 font-mono text-[10px] text-text-muted text-right">
                  {c.data_points}
                </span>
              </div>
            )
          )}
        </div>
      </div>

    </div>
  )
}