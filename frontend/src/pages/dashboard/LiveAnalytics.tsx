import { Activity, Wifi, RefreshCw, Clock } from 'lucide-react'
import { useState, useEffect, useCallback } from 'react'
import { useWorkforce } from '@/hooks/useWorkforce'
import { useSalary } from '@/hooks/useSalary'
import KpiCard, { fmtNumber, fmtUSD } from '@/components/dashboard/KpiCard'
import SectionHeader from '@/components/shared/SectionHeader'
import WorkforceHiringTrendChart from '@/components/workforce/WorkforceHiringTrendChart'

// ─────────────────────────────────────────
// LiveAnalytics
//
// Auto-refreshes every 30 seconds.
// Uses the same real API endpoints as other
// pages — polls them on an interval.
// Shows last-updated timestamp.
//
// Data sources:
//   /api/v1/workforce/hiring-trends
//   /api/v1/workforce/remote-stats
//   /api/v1/salary/trends
// ─────────────────────────────────────────

const REFRESH_INTERVAL_MS = 30_000 // 30 seconds

function useLastUpdated() {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const update = useCallback(() => setLastUpdated(new Date()), [])
  return { lastUpdated, update }
}

export default function LiveAnalytics() {
  const workforce = useWorkforce()
  const salary    = useSalary()
  const { lastUpdated, update } = useLastUpdated()
  const [refreshCount, setRefreshCount] = useState(0)
  const [countdown, setCountdown] = useState(REFRESH_INTERVAL_MS / 1000)

  // Trigger a data refresh by incrementing the counter
  // (hooks re-run their fetch when called, but since they
  // use useEffect on mount, we call refetch directly)
  const handleRefresh = useCallback(() => {
    workforce.refetch()
    salary.refetch()
    update()
    setCountdown(REFRESH_INTERVAL_MS / 1000)
    setRefreshCount(c => c + 1)
  }, [workforce, salary, update])

  // Auto-refresh interval
  useEffect(() => {
    const interval = setInterval(handleRefresh, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [handleRefresh])

  // Countdown timer
  useEffect(() => {
    const tick = setInterval(() => setCountdown(c => Math.max(0, c - 1)), 1000)
    return () => clearInterval(tick)
  }, [refreshCount])

  // Mark last updated once data loads
  useEffect(() => {
    if (workforce.status === 'success') update()
  }, [workforce.status, update])

  const isLoading = workforce.status === 'idle' || workforce.status === 'loading'
  const isSalaryLoading = salary.status === 'idle' || salary.status === 'loading'

  const totalPostings = workforce.data?.remoteStats.total_postings ?? 0
  const remotePct     = workforce.data?.remoteStats.remote_pct ?? 0
  const latestSalary  = salary.data?.trends[salary.data.trends.length - 1]

  return (
    <div className="space-y-5 page-enter">

      {/* Page heading */}
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-1">
            overview / live
          </p>
          <h1 className="text-2xl font-semibold text-text-primary tracking-tight">
            Live Analytics
          </h1>
          <p className="text-[13px] text-text-secondary mt-0.5">
            Real-time workforce metrics — auto-refreshes every 30s
          </p>
        </div>

        {/* Live status + manual refresh */}
        <div className="flex items-center gap-3 flex-shrink-0">
          {lastUpdated && (
            <div className="flex items-center gap-1.5">
              <Clock size={11} className="text-text-muted" />
              <span className="font-mono text-[10px] text-text-muted">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            </div>
          )}
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-md"
            style={{ background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.2)' }}>
            <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-dot" />
            <span className="font-mono text-[10px] text-success uppercase tracking-wider">
              Live · {countdown}s
            </span>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            aria-label="Refresh now"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px]
                       text-text-secondary border border-border hover:border-border-light
                       hover:text-text-primary transition-all duration-150 disabled:opacity-40"
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} aria-hidden="true" />
            Refresh
          </button>
        </div>
      </div>

      {/* Error banners */}
      {workforce.error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-danger"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)' }}>
          <span>⚠</span><span>Workforce API: {workforce.error}</span>
        </div>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Total Postings"
          value={isLoading ? '—' : fmtNumber(totalPostings)}
          delta="current year · 2024"
          trend="up"
          icon={Activity}
          isLoading={isLoading}
        />
        <KpiCard
          label="Remote Share"
          value={isLoading ? '—' : `${remotePct.toFixed(1)}%`}
          delta={`${fmtNumber(workforce.data?.remoteStats.remote_postings ?? 0)} remote`}
          trend="up"
          icon={Wifi}
          isLoading={isLoading}
        />
        <KpiCard
          label="Avg Salary (2024)"
          value={latestSalary && !isSalaryLoading ? fmtUSD(latestSalary.avg_salary_usd) : '—'}
          delta={latestSalary?.salary_growth_pct
            ? `+${latestSalary.salary_growth_pct.toFixed(1)}% YoY`
            : undefined}
          trend="up"
          icon={Activity}
          isLoading={isSalaryLoading}
        />
        <KpiCard
          label="Countries Tracked"
          value={isLoading ? '—' : String(workforce.data?.byCountry.length ?? 0)}
          delta={`${workforce.data?.byIndustry.length ?? 0} industries`}
          trend="neutral"
          icon={Activity}
          isLoading={isLoading}
        />
      </div>

      {/* Live hiring trend chart */}
      <WorkforceHiringTrendChart
        data={workforce.data?.hiringTrends ?? []}
        isLoading={isLoading}
      />

      {/* Live data table — top countries by postings */}
      <div className="kpi-card">
        <SectionHeader
          title="Live Country Rankings"
          subtitle="Hiring demand by country · polling every 30s"
          badge="LIVE"
        />
        <div className="grid grid-cols-12 gap-2 px-2 mb-1">
          {['#', 'Country', 'Region', 'Postings', 'Avg Salary'].map((h, i) => (
            <span key={h} className={`font-mono text-[10px] text-text-muted uppercase tracking-wider
              ${i === 0 ? 'col-span-1' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-3' : i === 3 ? 'col-span-2 text-right' : 'col-span-3 text-right'}`}>
              {h}
            </span>
          ))}
        </div>
        <div className="space-y-0.5">
          {(isLoading ? Array(8).fill(null) : (workforce.data?.byCountry ?? []).slice(0, 8)).map((c, i) =>
            isLoading ? (
              <div key={i} className="h-9 bg-base-700 rounded-lg animate-pulse" />
            ) : (
              <div key={c.country_name}
                className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                <span className="col-span-1 font-mono text-[11px] text-text-muted">{i + 1}</span>
                <span className="col-span-3 text-[12px] text-text-primary truncate">{c.country_name}</span>
                <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{c.region}</span>
                <span className="col-span-2 font-mono text-[11px] text-accent-DEFAULT text-right">
                  {fmtNumber(c.total_postings)}
                </span>
                <span className="col-span-3 font-mono text-[11px] text-text-secondary text-right">
                  {c.avg_salary_usd ? fmtUSD(c.avg_salary_usd) : '—'}
                </span>
              </div>
            )
          )}
        </div>
      </div>

    </div>
  )
}