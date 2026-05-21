import type { FutureSafeCareer } from '@/types/aiImpact'
import SectionHeader from '@/components/shared/SectionHeader'
import RiskMeter from '@/components/shared/RiskMeter'

interface Props { data: FutureSafeCareer[]; isLoading?: boolean }

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse space-y-2">
      <div className="h-4 w-40 bg-base-600 rounded mb-3" />
      {[...Array(6)].map((_, i) => <div key={i} className="h-10 bg-base-700 rounded-lg" />)}
    </div>
  )
}

export default function FutureSafeCareersTable({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Future-Safe Careers" subtitle="Ranked by safety from AI disruption · 2024" badge="TOP 8" />
      {/* Column headers */}
      <div className="grid grid-cols-12 gap-2 px-2 mb-1">
        <span className="col-span-1 font-mono text-[10px] text-text-muted">#</span>
        <span className="col-span-4 font-mono text-[10px] text-text-muted uppercase tracking-wider">Role</span>
        <span className="col-span-4 font-mono text-[10px] text-text-muted uppercase tracking-wider">Safe Score</span>
        <span className="col-span-2 font-mono text-[10px] text-text-muted uppercase tracking-wider text-right">Risk</span>
        <span className="col-span-1 font-mono text-[10px] text-text-muted text-center">🌐</span>
      </div>
      <div className="space-y-0.5">
        {data.map((r) => (
          <div key={r.rank}
            className="grid grid-cols-12 gap-2 items-center px-2 py-2.5 rounded-md hover:bg-base-700 transition-colors duration-150">
            <span className="col-span-1 font-mono text-[11px] text-text-muted">{r.rank}</span>
            <div className="col-span-4 min-w-0">
              <p className="text-[12px] text-text-primary truncate">{r.role_name}</p>
              <p className="font-mono text-[10px] text-text-muted truncate">{r.role_category}</p>
            </div>
            <div className="col-span-4">
              <RiskMeter value={r.avg_future_safe_score} variant="safe" size="sm" />
            </div>
            <span className="col-span-2 font-mono text-[11px] text-danger text-right">
              {r.ai_disruption_risk != null ? `${(r.ai_disruption_risk * 100).toFixed(0)}%` : '—'}
            </span>
            <span className="col-span-1 text-center text-[11px] text-text-muted">
              {r.is_remote_eligible ? '✓' : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}