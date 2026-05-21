import { TrendingUp, Calendar, BarChart2, AlertCircle } from 'lucide-react'
import PageHeader from '@/components/shared/PageHeader'
import PlaceholderPage from '@/components/shared/PlaceholderPage'
import { useSalary } from '@/hooks/useSalary'
import { useWorkforce } from '@/hooks/useWorkforce'
import KpiCard, { fmtUSD, fmtNumber } from '@/components/dashboard/KpiCard'
import SalaryTrendChart from '@/components/salary/SalaryTrendChart'
import WorkforceHiringTrendChart from '@/components/workforce/WorkforceHiringTrendChart'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// Forecasting
//
// Phase 5 page — shows real historical trend
// data now (salary + hiring trends from existing
// APIs as a foundation).
//
// Prophet/XGBoost forecast endpoints will be
// wired in Phase 5 when /api/v1/forecast/* is ready.
// ─────────────────────────────────────────

export default function Forecasting() {
  const salary    = useSalary()
  const workforce = useWorkforce()

  const isLoadingSalary    = salary.status === 'idle' || salary.status === 'loading'
  const isLoadingWorkforce = workforce.status === 'idle' || workforce.status === 'loading'

  const latestSalary  = salary.data?.trends[salary.data.trends.length - 1]
  const earliestSalary = salary.data?.trends[0]
  const latestHiring  = workforce.data?.hiringTrends[workforce.data.hiringTrends.length - 1]
  const earliestHiring = workforce.data?.hiringTrends[0]

  // Compute simple trend direction from historical data
  const salaryTrendPct = latestSalary && earliestSalary && earliestSalary.avg_salary_usd > 0
    ? (((latestSalary.avg_salary_usd - earliestSalary.avg_salary_usd) / earliestSalary.avg_salary_usd) * 100)
    : null

  const hiringTrendPct = latestHiring && earliestHiring && earliestHiring.total_postings > 0
    ? (((latestHiring.total_postings - earliestHiring.total_postings) / earliestHiring.total_postings) * 100)
    : null

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="predictive"
        title="Forecasting"
        description="Historical trends and AI-powered forecasts for hiring and salary"
        isLoading={isLoadingSalary || isLoadingWorkforce}
        onRefetch={() => { salary.refetch(); workforce.refetch() }}
      />

      {/* Phase 5 notice */}
      <div className="flex items-start gap-3 px-4 py-3 rounded-lg"
        style={{ background: 'rgba(129,140,248,0.08)', border: '1px solid rgba(129,140,248,0.2)' }}>
        <AlertCircle size={15} className="text-info flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-[13px] font-medium text-text-primary">Prophet forecasting coming in Phase 5</p>
          <p className="text-[12px] text-text-secondary mt-0.5">
            Historical data is shown below from live APIs. Predictive forecast charts will be added
            once <code className="font-mono text-[11px] text-accent-DEFAULT">/api/v1/forecast/*</code> endpoints are wired.
          </p>
        </div>
      </div>

      {/* KPI row — from real historical data */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="2024 Avg Salary"
          value={latestSalary && !isLoadingSalary ? fmtUSD(latestSalary.avg_salary_usd) : '—'}
          delta="current benchmark"
          trend="up"
          icon={TrendingUp}
          isLoading={isLoadingSalary}
        />
        <KpiCard
          label="Salary Growth (6yr)"
          value={salaryTrendPct && !isLoadingSalary ? `+${salaryTrendPct.toFixed(1)}%` : '—'}
          delta="2018 → 2024 cumulative"
          trend="up"
          icon={BarChart2}
          isLoading={isLoadingSalary}
        />
        <KpiCard
          label="2024 Job Postings"
          value={latestHiring && !isLoadingWorkforce ? fmtNumber(latestHiring.total_postings) : '—'}
          delta="current volume"
          trend="up"
          icon={Calendar}
          isLoading={isLoadingWorkforce}
        />
        <KpiCard
          label="Hiring Growth (6yr)"
          value={hiringTrendPct && !isLoadingWorkforce ? `+${hiringTrendPct.toFixed(1)}%` : '—'}
          delta="2018 → 2024 cumulative"
          trend="up"
          icon={TrendingUp}
          isLoading={isLoadingWorkforce}
        />
      </div>

      {/* Historical trend charts — foundation for forecast overlay */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <SalaryTrendChart data={salary.data?.trends ?? []} isLoading={isLoadingSalary} />
        <WorkforceHiringTrendChart data={workforce.data?.hiringTrends ?? []} isLoading={isLoadingWorkforce} />
      </div>

      {/* Forecast placeholder — Phase 5 */}
      <div className="kpi-card">
        <SectionHeader
          title="AI Forecast Charts"
          subtitle="Prophet + XGBoost predictions · Available in Phase 5"
          badge="COMING SOON"
        />
        <div className="flex flex-col items-center justify-center py-12 gap-3">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: 'rgba(129,140,248,0.08)', border: '1px solid rgba(129,140,248,0.2)' }}>
            <TrendingUp size={20} className="text-info" />
          </div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted">Phase 5</p>
          <p className="text-[13px] text-text-secondary text-center max-w-xs">
            Predictive hiring & salary forecast charts powered by Prophet and XGBoost will render here.
          </p>
        </div>
      </div>
    </div>
  )
}