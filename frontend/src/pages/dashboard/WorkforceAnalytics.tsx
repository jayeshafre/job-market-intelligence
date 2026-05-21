import { Users, Briefcase, Globe, Wifi } from 'lucide-react'
import { useWorkforce } from '@/hooks/useWorkforce'
import PageHeader from '@/components/shared/PageHeader'
import KpiCard, { fmtNumber, fmtUSD } from '@/components/dashboard/KpiCard'
import WorkforceHiringTrendChart from '@/components/workforce/WorkforceHiringTrendChart'
import TopRolesTable from '@/components/workforce/TopRolesTable'
import TopIndustriesWidget from '@/components/dashboard/TopIndustriesWidget'
import TopCountriesWidget from '@/components/dashboard/TopCountriesWidget'
import RemoteSplitWidget from '@/components/dashboard/RemoteSplitWidget'

// ─────────────────────────────────────────
// WorkforceAnalytics — fully connected to live API
//
// AUDIT FIX 1: Removed fabricated hybrid_pct calculation.
//   Was: hybrid_pct: Math.round((100 - remote_pct) * 0.52)
//   Fix: RemoteSplitWidget now accepts RemoteBreakdown directly.
//        No hybrid field — backend doesn't have it.
//
// AUDIT FIX 2: Removed growth_pct: ai_adoption_index * 20.
//   Was: passing a fake % to TopIndustriesWidget.
//   Fix: TopIndustriesWidget now accepts IndustryHiringStats
//        directly and shows ai_adoption_index correctly.
//
// AUDIT FIX 3: TopCountriesWidget now typed to CountryHiringStats.
//   Shows real total_postings, not an invented job_count.
// ─────────────────────────────────────────

export default function WorkforceAnalytics() {
  const { data, status, error, refetch } = useWorkforce()
  const isLoading = status === 'idle' || status === 'loading'

  // All KPI values derived from real API fields
  const totalPostings  = data?.remoteStats.total_postings ?? 0
  const remotePct      = data?.remoteStats.remote_pct ?? 0
  const topCountry     = data?.byCountry[0]?.country_name ?? '—'
  const topAvgSalary   = data?.byCountry[0]?.avg_salary_usd ?? null
  const countriesCount = data?.byCountry.length ?? 0

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="intelligence"
        title="Workforce Analytics"
        description="Hiring demand, industry growth, remote work adoption, and role rankings"
        isLoading={isLoading}
        onRefetch={refetch}
      />

      {error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-danger"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)' }}>
          <span>⚠</span><span>Could not reach backend: {error}</span>
        </div>
      )}

      {/* KPI row — all from real data fields */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Total Postings"
          value={isLoading ? '—' : fmtNumber(totalPostings)}
          delta={`${countriesCount} countries tracked`}
          trend="up"
          icon={Briefcase}
          isLoading={isLoading}
        />
        <KpiCard
          label="Remote Share"
          value={isLoading ? '—' : `${remotePct.toFixed(1)}%`}
          delta={`${fmtNumber(data?.remoteStats.remote_postings ?? 0)} remote postings`}
          trend="up"
          icon={Wifi}
          isLoading={isLoading}
        />
        <KpiCard
          label="Top Country"
          value={isLoading ? '—' : topCountry}
          delta="by posting volume"
          trend="neutral"
          icon={Globe}
          isLoading={isLoading}
        />
        <KpiCard
          label="Top Country Salary"
          value={isLoading || !topAvgSalary ? '—' : fmtUSD(topAvgSalary)}
          delta="avg salary (USD)"
          trend="up"
          icon={Users}
          isLoading={isLoading}
        />
      </div>

      {/* Trend + remote split */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          {/* WorkforceHiringTrendChart uses: year, total_postings, remote_postings */}
          <WorkforceHiringTrendChart data={data?.hiringTrends ?? []} isLoading={isLoading} />
        </div>
        {/* AUDIT FIX: pass RemoteBreakdown directly — no invented hybrid_pct */}
        <RemoteSplitWidget
          data={data?.remoteStats ?? { total_postings: 0, remote_postings: 0, onsite_postings: 0, remote_pct: 0 }}
          isLoading={isLoading}
        />
      </div>

      {/* Industries + top roles */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* AUDIT FIX: pass IndustryHiringStats directly — no fabricated growth_pct */}
        <TopIndustriesWidget data={data?.byIndustry ?? []} isLoading={isLoading} />
        <TopRolesTable data={data?.topRoles ?? []} isLoading={isLoading} />
      </div>

      {/* Country table */}
      {/* AUDIT FIX: pass CountryHiringStats directly with mode="postings" */}
      <TopCountriesWidget data={data?.byCountry ?? []} isLoading={isLoading} mode="postings" />
    </div>
  )
}