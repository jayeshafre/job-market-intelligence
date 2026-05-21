import { Briefcase, DollarSign, Globe, Bot, RefreshCw } from 'lucide-react'
import { useDashboardStats } from '@/hooks/useDashboardStats'
import KpiCard, { fmtNumber, fmtUSD, fmtPct } from '@/components/dashboard/KpiCard'
import HiringTrendChart from '@/components/dashboard/HiringTrendChart'
import TopIndustriesWidget from '@/components/dashboard/TopIndustriesWidget'
import TopCountriesWidget from '@/components/dashboard/TopCountriesWidget'
import RemoteSplitWidget from '@/components/dashboard/RemoteSplitWidget'

// ─────────────────────────────────────────
// MainDashboard — fully connected to live API
//
// Data flow:
//   fetchDashboardData() [analyticsService]
//     → 7 parallel API calls (all real endpoints)
//     → deriveKpi() computes KpiSummary from real data
//     → useDashboardStats hook stores in state
//     → this component renders it
//
// Layout:
//   Row 1 — 4 KPI cards (from deriveKpi)
//   Row 2 — HiringTrendChart (total_postings) + RemoteSplitWidget
//   Row 3 — TopIndustriesWidget + TopCountriesWidget
// ─────────────────────────────────────────

export default function MainDashboard() {
  const { data, status, error, refetch } = useDashboardStats()
  const isLoading = status === 'loading' || status === 'idle'

  return (
    <div className="space-y-5 page-enter">

      {/* Page heading */}
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-1">overview</p>
          <h1 className="text-2xl font-semibold text-text-primary tracking-tight">Main Dashboard</h1>
          <p className="text-[13px] text-text-secondary mt-0.5">
            Global workforce intelligence — key metrics at a glance
          </p>
        </div>
        <button
          onClick={refetch}
          disabled={isLoading}
          aria-label="Refresh dashboard data"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] text-text-secondary
                     border border-border hover:border-border-light hover:text-text-primary
                     transition-all duration-150 disabled:opacity-40"
        >
          <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-danger"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)' }}>
          <span>⚠</span>
          <span>Could not reach backend: {error}</span>
        </div>
      )}

      {/* Row 1 — KPI cards (all from real derived data) */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Total Job Postings"
          value={data ? fmtNumber(data.kpi.total_job_postings) : '—'}
          delta={data ? `+${fmtPct(data.kpi.yoy_job_growth_pct)} YoY` : undefined}
          trend="up"
          icon={Briefcase}
          isLoading={isLoading}
        />
        <KpiCard
          label="Avg. Salary (USD)"
          value={data ? fmtUSD(data.kpi.avg_salary_usd) : '—'}
          delta={data?.kpi.yoy_salary_growth_pct
            ? `+${fmtPct(data.kpi.yoy_salary_growth_pct)} YoY`
            : undefined}
          trend="up"
          icon={DollarSign}
          isLoading={isLoading}
        />
        <KpiCard
          label="Countries · Industries"
          value={data ? `${data.kpi.total_countries} · ${data.kpi.total_industries}` : '—'}
          delta="tracked globally"
          trend="neutral"
          icon={Globe}
          isLoading={isLoading}
        />
        <KpiCard
          label="AI Disruption Index"
          value={data ? data.kpi.ai_disruption_index.toFixed(2) : '—'}
          delta={data ? `Top skill: ${data.kpi.top_growing_skill}` : undefined}
          trend="down"
          icon={Bot}
          isLoading={isLoading}
        />
      </div>

      {/* Row 2 — Hiring trend + remote split */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          {/* data.hiringTrend has real fields: year, total_postings, remote_postings */}
          <HiringTrendChart data={data?.hiringTrend ?? []} isLoading={isLoading} />
        </div>
        <div>
          {/* data.remoteSplit has real fields: total_postings, remote_postings, onsite_postings, remote_pct */}
          <RemoteSplitWidget
            data={data?.remoteSplit ?? { total_postings: 0, remote_postings: 0, onsite_postings: 0, remote_pct: 0 }}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Row 3 — Industries + Countries */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* data.topIndustries has: industry_name, sector, total_postings, ai_adoption_index */}
        <TopIndustriesWidget data={data?.topIndustries ?? []} isLoading={isLoading} />
        {/* data.topCountries has: country_name, region, total_postings, avg_salary_usd */}
        <TopCountriesWidget data={data?.topCountries ?? []} isLoading={isLoading} mode="postings" />
      </div>

    </div>
  )
}