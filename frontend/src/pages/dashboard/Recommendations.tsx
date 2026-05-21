import { Sparkles, Brain, TrendingUp, ShieldCheck, AlertCircle } from 'lucide-react'
import PageHeader from '@/components/shared/PageHeader'
import SectionHeader from '@/components/shared/SectionHeader'
import { useSkills } from '@/hooks/useSkills'
import { useAiImpact } from '@/hooks/useAiImpact'
import { useSalary } from '@/hooks/useSalary'
import KpiCard, { fmtUSD } from '@/components/dashboard/KpiCard'
import RiskMeter from '@/components/shared/RiskMeter'

// ─────────────────────────────────────────
// Recommendations
//
// Surfaces AI-generated insights by composing
// data from 3 real APIs:
//   /api/v1/skills/top-growing     → skill recommendations
//   /api/v1/ai-impact/future-safe-careers → career safety
//   /api/v1/salary/top-paying-roles       → salary opportunity
//
// Full AI-generated recommendation text will
// come from /api/v1/ai/* in Phase 4.
// ─────────────────────────────────────────

export default function Recommendations() {
  const skills    = useSkills()
  const aiImpact  = useAiImpact()
  const salary    = useSalary()

  const isLoading = skills.status === 'idle' || skills.status === 'loading'
  const isAiLoading = aiImpact.status === 'idle' || aiImpact.status === 'loading'
  const isSalaryLoading = salary.status === 'idle' || salary.status === 'loading'

  const topSkills     = skills.data?.topGrowing.slice(0, 5) ?? []
  const safeCareers   = aiImpact.data?.futureSafeCareers.slice(0, 5) ?? []
  const topRoles      = salary.data?.topRoles.slice(0, 5) ?? []

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="predictive"
        title="Recommendations"
        description="AI-derived career insights from real workforce, skills, and salary data"
        isLoading={isLoading}
        onRefetch={() => { skills.refetch(); aiImpact.refetch(); salary.refetch() }}
      />

      {/* Phase 4 notice */}
      <div className="flex items-start gap-3 px-4 py-3 rounded-lg"
        style={{ background: 'rgba(129,140,248,0.08)', border: '1px solid rgba(129,140,248,0.2)' }}>
        <AlertCircle size={15} className="text-info flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-[13px] font-medium text-text-primary">Personalised AI recommendations in Phase 4</p>
          <p className="text-[12px] text-text-secondary mt-0.5">
            Data-driven insight cards are live now. Natural language recommendations from the Groq AI assistant
            will be added in Phase 4 via <code className="font-mono text-[11px] text-accent-DEFAULT">/api/v1/ai/*</code>.
          </p>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
        <KpiCard
          label="Top Skill to Learn"
          value={topSkills[0] && !isLoading ? topSkills[0].skill_name : '—'}
          delta={topSkills[0]?.growth_pct ? `+${topSkills[0].growth_pct.toFixed(1)}% demand growth` : undefined}
          trend="up"
          icon={Brain}
          isLoading={isLoading}
        />
        <KpiCard
          label="Safest Career Path"
          value={safeCareers[0] && !isAiLoading ? safeCareers[0].role_name : '—'}
          delta={safeCareers[0]?.avg_future_safe_score
            ? `${(safeCareers[0].avg_future_safe_score * 100).toFixed(0)}% future-safe`
            : undefined}
          trend="up"
          icon={ShieldCheck}
          isLoading={isAiLoading}
        />
        <KpiCard
          label="Highest Salary Role"
          value={topRoles[0] && !isSalaryLoading ? topRoles[0].role_name : '—'}
          delta={topRoles[0] ? fmtUSD(topRoles[0].avg_salary_usd) : undefined}
          trend="up"
          icon={TrendingUp}
          isLoading={isSalaryLoading}
        />
      </div>

      {/* Three insight panels side by side */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">

        {/* Skill recommendations */}
        <div className="kpi-card">
          <SectionHeader title="Skills to Prioritise" subtitle="Top growing skills · 2024" />
          <div className="space-y-3">
            {(isLoading ? Array(5).fill(null) : topSkills).map((s, i) =>
              isLoading ? (
                <div key={i} className="h-12 bg-base-700 rounded-lg animate-pulse" />
              ) : (
                <div key={s.skill_name} className="flex items-center justify-between p-2.5 rounded-lg bg-base-700">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-[12px] font-medium text-text-primary truncate">{s.skill_name}</p>
                      {s.is_ai_related && (
                        <span className="font-mono text-[9px] px-1.5 rounded flex-shrink-0"
                          style={{ background: 'rgba(34,211,238,0.1)', color: '#22D3EE', border: '1px solid rgba(34,211,238,0.2)' }}>
                          AI
                        </span>
                      )}
                    </div>
                    <p className="font-mono text-[10px] text-text-muted mt-0.5">{s.skill_category}</p>
                  </div>
                  <span className="font-mono text-[11px] text-success flex-shrink-0 ml-2">
                    +{s.growth_pct?.toFixed(1)}%
                  </span>
                </div>
              )
            )}
          </div>
        </div>

        {/* Safe career recommendations */}
        <div className="kpi-card">
          <SectionHeader title="Future-Safe Careers" subtitle="AI disruption risk ranking · 2024" />
          <div className="space-y-3">
            {(isAiLoading ? Array(5).fill(null) : safeCareers).map((c, i) =>
              isAiLoading ? (
                <div key={i} className="h-12 bg-base-700 rounded-lg animate-pulse" />
              ) : (
                <div key={c.role_name} className="p-2.5 rounded-lg bg-base-700">
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="text-[12px] font-medium text-text-primary truncate">{c.role_name}</p>
                    <span className="font-mono text-[10px] text-text-muted flex-shrink-0 ml-2">#{c.rank}</span>
                  </div>
                  <RiskMeter value={c.avg_future_safe_score} variant="safe" size="sm" />
                </div>
              )
            )}
          </div>
        </div>

        {/* Salary opportunity */}
        <div className="kpi-card">
          <SectionHeader title="Highest Salary Roles" subtitle="Top-paying positions · 2024" />
          <div className="space-y-3">
            {(isSalaryLoading ? Array(5).fill(null) : topRoles).map((r, i) =>
              isSalaryLoading ? (
                <div key={i} className="h-12 bg-base-700 rounded-lg animate-pulse" />
              ) : (
                <div key={r.role_name} className="flex items-center justify-between p-2.5 rounded-lg bg-base-700">
                  <div className="min-w-0">
                    <p className="text-[12px] font-medium text-text-primary truncate">{r.role_name}</p>
                    <p className="font-mono text-[10px] text-text-muted mt-0.5">{r.seniority_level}</p>
                  </div>
                  <span className="font-mono text-[12px] text-accent-DEFAULT flex-shrink-0 ml-2 font-medium">
                    {fmtUSD(r.avg_salary_usd)}
                  </span>
                </div>
              )
            )}
          </div>
        </div>

      </div>
    </div>
  )
}