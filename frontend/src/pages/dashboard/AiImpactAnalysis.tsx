import { Bot, ShieldCheck, AlertTriangle, Factory } from 'lucide-react'
import { useAiImpact } from '@/hooks/useAiImpact'
import PageHeader from '@/components/shared/PageHeader'
import KpiCard from '@/components/dashboard/KpiCard'
import DisruptionTrendChart from '@/components/ai-impact/DisruptionTrendChart'
import FutureSafeCareersTable from '@/components/ai-impact/FutureSafeCareersTable'
import SectionHeader from '@/components/shared/SectionHeader'
import RiskMeter from '@/components/shared/RiskMeter'

export default function AiImpactAnalysis() {
  const { data, status, error, refetch } = useAiImpact()
  const isLoading = status === 'idle' || status === 'loading'

  const latestTrend   = data?.trends[data.trends.length - 1]
  const avgRisk       = latestTrend?.avg_automation_risk ?? null
  const avgSafe       = latestTrend?.avg_future_safe ?? null
  const avgReplacement = latestTrend?.avg_ai_replacement ?? null
  const highestRiskIndustry = data?.byIndustry.slice().sort(
    (a, b) => (b.avg_automation_risk ?? 0) - (a.avg_automation_risk ?? 0)
  )[0]

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="intelligence"
        title="AI Impact Analysis"
        description="Automation risk, AI disruption scores, and future-safe career rankings"
        isLoading={isLoading}
        onRefetch={refetch}
      />

      {error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[13px] text-warning"
          style={{ background: 'rgba(249,115,22,0.08)', border: '1px solid rgba(249,115,22,0.2)' }}>
          <span>⚠</span><span>{error} — showing cached data.</span>
        </div>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard label="Avg Automation Risk"   value={avgRisk    && !isLoading ? `${(avgRisk * 100).toFixed(0)}%`       : '—'} delta="global average 2024"    trend="down"    icon={AlertTriangle} isLoading={isLoading} />
        <KpiCard label="Avg Future Safe Score" value={avgSafe    && !isLoading ? `${(avgSafe * 100).toFixed(0)}%`        : '—'} delta="global average 2024"    trend="up"      icon={ShieldCheck}   isLoading={isLoading} />
        <KpiCard label="AI Replacement Index"  value={avgReplacement && !isLoading ? `${(avgReplacement * 100).toFixed(0)}%` : '—'} delta="avg across all roles" trend="down" icon={Bot}           isLoading={isLoading} />
        <KpiCard label="Most At-Risk Industry" value={highestRiskIndustry && !isLoading ? highestRiskIndustry.industry_name : '—'} delta={highestRiskIndustry ? `${((highestRiskIndustry.avg_automation_risk ?? 0) * 100).toFixed(0)}% risk` : undefined} trend="down" icon={Factory} isLoading={isLoading} />
      </div>

      {/* Trend chart + future safe careers */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <DisruptionTrendChart data={data?.trends ?? []} isLoading={isLoading} />
        <FutureSafeCareersTable data={data?.futureSafeCareers ?? []} isLoading={isLoading} />
      </div>

      {/* Industry disruption table */}
      <div className="kpi-card page-enter">
        <SectionHeader title="AI Disruption by Industry" subtitle="Automation risk & future-safe scores per industry · 2024" />
        <div className="grid grid-cols-12 gap-2 px-2 mb-1">
          {['Industry', 'Sector', 'Automation Risk', 'Future Safe', 'AI Adoption'].map((h, i) => (
            <span key={h} className={`font-mono text-[10px] text-text-muted uppercase tracking-wider
              ${i === 0 ? 'col-span-3' : i === 1 ? 'col-span-2' : 'col-span-2 text-center'}`}>{h}</span>
          ))}
          <span className="col-span-1" />
        </div>
        <div className="space-y-0.5">
          {(isLoading ? Array(6).fill(null) : (data?.byIndustry ?? [])).map((ind, i) =>
            isLoading ? (
              <div key={i} className="h-10 bg-base-700 rounded-lg animate-pulse" />
            ) : (
              <div key={ind.industry_name} className="grid grid-cols-12 gap-2 items-center px-2 py-2.5 rounded-md hover:bg-base-700 transition-colors duration-150">
                <span className="col-span-3 text-[12px] text-text-primary truncate">{ind.industry_name}</span>
                <span className="col-span-2 font-mono text-[11px] text-text-muted truncate">{ind.sector}</span>
                <div className="col-span-2">
                  <RiskMeter value={ind.avg_automation_risk} variant="risk" size="sm" />
                </div>
                <div className="col-span-2">
                  <RiskMeter value={ind.avg_future_safe} variant="safe" size="sm" />
                </div>
                <div className="col-span-2">
                  <RiskMeter value={ind.ai_adoption_index} variant="safe" size="sm" />
                </div>
                <span className="col-span-1 font-mono text-[10px] text-text-muted text-right">
                  {ind.ai_adoption_index.toFixed(2)}
                </span>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  )
}