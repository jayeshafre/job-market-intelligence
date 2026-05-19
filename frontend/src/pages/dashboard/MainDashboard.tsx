import {
  Briefcase, DollarSign, Globe, Brain, Bot, RefreshCw,
} from 'lucide-react'
import { useDashboardStats } from '@/hooks/useDashboardStats'
import KpiCard, { fmtNumber, fmtUSD, fmtPct } from '@/components/dashboard/KpiCard'
import HiringTrendChart from '@/components/dashboard/HiringTrendChart'
import TopIndustriesWidget from '@/components/dashboard/TopIndustriesWidget'
import TopCountriesWidget from '@/components/dashboard/TopCountriesWidget'
import RemoteSplitWidget from '@/components/dashboard/RemoteSplitWidget'

// ─────────────────────────────────────────
// MainDashboard
//
// Layout (3-row grid):
//
//  Row 1: 4 KPI cards
//  Row 2: Hiring Trend chart (wide) + Remote Split (narrow)
//  Row 3: Top Industries + Top Countries
//
// All data fetched via useDashboardStats()
// which calls analyticsService in parallel.
// ─────────────────────────────────────────

export default function MainDashboard() {
  const { data, status, error, refetch } = useDashboardStats()
  const isLoading = status === 'loading' || status === 'idle'

  return (
    <div className="space-y-5 page-enter">

      {/* ── Page heading ── */}
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-1">
            overview
          </p>
          <h1 className="text-2xl font-semibold text-text-primary tracking-tight">
            Main Dashboard
          </h1>
          <p className="text-[13px] text-text-secondary mt-0.5">
            Global workforce intelligence — key metrics at a glance
          </p>
        </div>

        {/* Refetch button */}
        <button
          onClick={refetch}
          disabled={isLoading}
          aria-label="Refresh dashboard data"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] text-text-secondary
                     border border-border hover:border-border-light hover:text-text-primary
                     transition-all duration-150 disabled:opacity-40"
        >
          <RefreshCw
            size={13}
            className={isLoading ? 'animate-spin' : ''}
            aria-hidden="true"
          />
          Refresh
        </button>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-warning"
          style={{ background: 'rgba(249,115,22,0.08)', border: '1px solid rgba(249,115,22,0.2)' }}
        >
          <span>⚠</span>
          <span>{error} — showing cached data.</span>
        </div>
      )}

      {/* ── Row 1: KPI cards ── */}
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
          delta={data ? `+${fmtPct(data.kpi.yoy_salary_growth_pct)} YoY` : undefined}
          trend="up"
          icon={DollarSign}
          isLoading={isLoading}
        />
        <KpiCard
          label="Countries Tracked"
          value={data ? String(data.kpi.total_countries) : '—'}
          delta={`${data?.kpi.total_industries ?? '—'} industries`}
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

      {/* ── Row 2: Hiring trend + Remote split ── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Line chart — takes 2/3 width on xl */}
        <div className="xl:col-span-2">
          <HiringTrendChart
            data={data?.hiringTrend ?? []}
            isLoading={isLoading}
          />
        </div>

        {/* Donut widget — takes 1/3 width on xl */}
        <div>
          <RemoteSplitWidget
            data={data?.remoteSplit ?? { remote_pct: 0, hybrid_pct: 0, onsite_pct: 0 }}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* ── Row 3: Top industries + Top countries ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <TopIndustriesWidget
          data={data?.topIndustries ?? []}
          isLoading={isLoading}
        />
        <TopCountriesWidget
          data={data?.topCountries ?? []}
          isLoading={isLoading}
        />
      </div>

    </div>
  )
}