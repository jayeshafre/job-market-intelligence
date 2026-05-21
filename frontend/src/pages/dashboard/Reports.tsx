import { FileBarChart, Download, Calendar, TrendingUp, Users, Brain } from 'lucide-react'
import PageHeader from '@/components/shared/PageHeader'
import SectionHeader from '@/components/shared/SectionHeader'
import { useWorkforce } from '@/hooks/useWorkforce'
import { useSalary } from '@/hooks/useSalary'
import { useSkills } from '@/hooks/useSkills'
import { useAiImpact } from '@/hooks/useAiImpact'
import KpiCard, { fmtNumber, fmtUSD } from '@/components/dashboard/KpiCard'

// ─────────────────────────────────────────
// Reports
//
// Summary report view — pulls live data from
// all four API groups and presents digestible
// written summaries per domain.
//
// Full PDF/export functionality comes in Phase 5.
// ─────────────────────────────────────────

interface ReportCardProps {
  icon: React.ElementType
  title: string
  domain: string
  endpoint: string
  stats: { label: string; value: string }[]
  insights: string[]
  isLoading: boolean
}

function ReportCard({ icon: Icon, title, domain, endpoint, stats, insights, isLoading }: ReportCardProps) {
  if (isLoading) {
    return (
      <div className="kpi-card animate-pulse space-y-3">
        <div className="h-4 w-40 bg-base-600 rounded" />
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => <div key={i} className="h-3 bg-base-600 rounded" style={{ width: `${80 - i * 15}%` }} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="kpi-card space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.18)' }}>
            <Icon size={15} className="text-accent-DEFAULT" />
          </div>
          <div>
            <p className="text-[13px] font-semibold text-text-primary">{title}</p>
            <p className="font-mono text-[10px] text-text-muted">{domain}</p>
          </div>
        </div>
        <span className="font-mono text-[9px] text-accent-DEFAULT px-2 py-1 rounded"
          style={{ background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.15)' }}>
          {endpoint}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2">
        {stats.map(s => (
          <div key={s.label} className="bg-base-700 rounded-lg px-3 py-2">
            <p className="font-mono text-[9px] text-text-muted uppercase tracking-wider mb-0.5">{s.label}</p>
            <p className="font-mono text-[14px] font-semibold text-text-primary">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Insight bullets — derived from real data */}
      <div className="space-y-1.5 border-t border-border pt-3">
        {insights.map((ins, i) => (
          <div key={i} className="flex items-start gap-2">
            <div className="w-1 h-1 rounded-full bg-accent-DEFAULT flex-shrink-0 mt-1.5" />
            <p className="text-[12px] text-text-secondary leading-relaxed">{ins}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Reports() {
  const workforce = useWorkforce()
  const salary    = useSalary()
  const skills    = useSkills()
  const aiImpact  = useAiImpact()

  const isWLoading = workforce.status === 'idle' || workforce.status === 'loading'
  const isSLoading = salary.status    === 'idle' || salary.status    === 'loading'
  const isSkLoading = skills.status   === 'idle' || skills.status    === 'loading'
  const isALoading = aiImpact.status  === 'idle' || aiImpact.status  === 'loading'

  // ── Derive real insight strings from live data ──

  const topCountry      = workforce.data?.byCountry[0]
  const topIndustry     = workforce.data?.byIndustry[0]
  const remotePct       = workforce.data?.remoteStats.remote_pct
  const totalPostings   = workforce.data?.remoteStats.total_postings

  const latestSalary    = salary.data?.trends[salary.data.trends.length - 1]
  const topPayRole      = salary.data?.topRoles[0]
  const topPayCountry   = salary.data?.topCountries[0]

  const topSkill        = skills.data?.topGrowing[0]
  const topAiSkill      = skills.data?.aiSkills[0]
  const aiCategoryCount = skills.data?.byCategory.length

  const latestRisk      = aiImpact.data?.trends[aiImpact.data.trends.length - 1]
  const safestCareer    = aiImpact.data?.futureSafeCareers[0]
  const riskiestInd     = aiImpact.data?.byIndustry
    .slice().sort((a, b) => (b.avg_automation_risk ?? 0) - (a.avg_automation_risk ?? 0))[0]

  const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="data"
        title="Reports"
        description="Live analytics summaries across all workforce intelligence domains"
        isLoading={isWLoading && isSLoading}
        onRefetch={() => {
          workforce.refetch(); salary.refetch()
          skills.refetch();    aiImpact.refetch()
        }}
      />

      {/* Report meta */}
      <div className="flex items-center justify-between px-4 py-3 rounded-lg bg-base-800 border border-border">
        <div className="flex items-center gap-2">
          <Calendar size={13} className="text-text-muted" />
          <span className="font-mono text-[11px] text-text-muted">Generated: {today}</span>
          <span className="font-mono text-[11px] text-text-muted mx-2">·</span>
          <span className="font-mono text-[11px] text-text-muted">Data year: 2024</span>
          <span className="font-mono text-[11px] text-text-muted mx-2">·</span>
          <span className="font-mono text-[11px] text-text-muted">Source: Live API</span>
        </div>
        <button
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] text-text-muted
                     border border-border hover:border-border-light hover:text-text-primary
                     transition-all duration-150 font-mono"
          title="PDF export available in Phase 5"
        >
          <Download size={12} />
          Export PDF
        </button>
      </div>

      {/* Summary KPI strip */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Total Job Postings"
          value={totalPostings && !isWLoading ? fmtNumber(totalPostings) : '—'}
          delta="2024 global total"
          trend="up"
          icon={Users}
          isLoading={isWLoading}
        />
        <KpiCard
          label="Avg Global Salary"
          value={latestSalary && !isSLoading ? fmtUSD(latestSalary.avg_salary_usd) : '—'}
          delta={latestSalary?.salary_growth_pct
            ? `+${latestSalary.salary_growth_pct.toFixed(1)}% YoY`
            : undefined}
          trend="up"
          icon={TrendingUp}
          isLoading={isSLoading}
        />
        <KpiCard
          label="Top Growing Skill"
          value={topSkill && !isSkLoading ? topSkill.skill_name : '—'}
          delta={topSkill?.growth_pct ? `+${topSkill.growth_pct.toFixed(1)}% demand` : undefined}
          trend="up"
          icon={Brain}
          isLoading={isSkLoading}
        />
        <KpiCard
          label="Automation Risk Index"
          value={latestRisk && !isALoading ? `${((latestRisk.avg_automation_risk ?? 0) * 100).toFixed(0)}%` : '—'}
          delta="global avg 2024"
          trend="down"
          icon={FileBarChart}
          isLoading={isALoading}
        />
      </div>

      {/* Domain report cards */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">

        <ReportCard
          icon={Users}
          title="Workforce Intelligence Report"
          domain="workforce analytics"
          endpoint="/workforce/*"
          isLoading={isWLoading}
          stats={[
            { label: 'Total Postings', value: totalPostings ? fmtNumber(totalPostings) : '—' },
            { label: 'Remote Share',   value: remotePct    ? `${remotePct.toFixed(1)}%`  : '—' },
            { label: 'Top Country',    value: topCountry   ? topCountry.country_name      : '—' },
            { label: 'Top Industry',   value: topIndustry  ? topIndustry.industry_name    : '—' },
          ]}
          insights={[
            topCountry
              ? `${topCountry.country_name} leads hiring with ${fmtNumber(topCountry.total_postings)} postings and avg salary of ${topCountry.avg_salary_usd ? fmtUSD(topCountry.avg_salary_usd) : '—'}.`
              : 'Country hiring data loading…',
            remotePct != null
              ? `${remotePct.toFixed(1)}% of all positions are remote, reflecting continued adoption of distributed work.`
              : 'Remote work data loading…',
            topIndustry
              ? `${topIndustry.industry_name} (${topIndustry.sector}) is the most active hiring sector with an AI adoption index of ${topIndustry.ai_adoption_index.toFixed(2)}.`
              : 'Industry data loading…',
          ]}
        />

        <ReportCard
          icon={TrendingUp}
          title="Salary Intelligence Report"
          domain="salary analytics"
          endpoint="/salary/*"
          isLoading={isSLoading}
          stats={[
            { label: 'Avg Salary 2024',    value: latestSalary   ? fmtUSD(latestSalary.avg_salary_usd)   : '—' },
            { label: 'YoY Growth',         value: latestSalary?.salary_growth_pct ? `+${latestSalary.salary_growth_pct.toFixed(1)}%` : '—' },
            { label: 'Top Paying Role',    value: topPayRole     ? topPayRole.role_name                  : '—' },
            { label: 'Top Paying Country', value: topPayCountry  ? topPayCountry.country_name            : '—' },
          ]}
          insights={[
            latestSalary
              ? `Global average salary reached ${fmtUSD(latestSalary.avg_salary_usd)} in 2024${latestSalary.salary_growth_pct ? `, growing ${latestSalary.salary_growth_pct.toFixed(1)}% year-over-year` : ''}.`
              : 'Salary trend data loading…',
            topPayRole
              ? `${topPayRole.role_name} is the highest compensated role at ${fmtUSD(topPayRole.avg_salary_usd)} average.`
              : 'Role salary data loading…',
            topPayCountry
              ? `${topPayCountry.country_name} offers the highest average compensation globally at ${fmtUSD(topPayCountry.avg_salary_usd)}.`
              : 'Country salary data loading…',
          ]}
        />

        <ReportCard
          icon={Brain}
          title="Skill Intelligence Report"
          domain="skill analytics"
          endpoint="/skills/*"
          isLoading={isSkLoading}
          stats={[
            { label: 'Top Growing Skill', value: topSkill      ? topSkill.skill_name                          : '—' },
            { label: 'Growth Rate',       value: topSkill?.growth_pct ? `+${topSkill.growth_pct.toFixed(1)}%` : '—' },
            { label: 'Top AI Skill',      value: topAiSkill    ? topAiSkill.skill_name                        : '—' },
            { label: 'Skill Categories',  value: aiCategoryCount ? String(aiCategoryCount)                    : '—' },
          ]}
          insights={[
            topSkill
              ? `${topSkill.skill_name} is the fastest growing skill in ${topSkill.skill_category} with +${topSkill.growth_pct?.toFixed(1)}% YoY demand growth.`
              : 'Skill data loading…',
            topAiSkill
              ? `${topAiSkill.skill_name} leads AI/ML skills with a demand score of ${topAiSkill.avg_demand_score?.toFixed(1)} and ${topAiSkill.total_mentions ? fmtNumber(topAiSkill.total_mentions) : 'many'} mentions.`
              : 'AI skill data loading…',
            aiCategoryCount
              ? `Skills span ${aiCategoryCount} categories, with AI/ML showing the highest cross-category growth momentum.`
              : 'Category data loading…',
          ]}
        />

        <ReportCard
          icon={FileBarChart}
          title="AI Impact Analysis Report"
          domain="ai disruption analytics"
          endpoint="/ai-impact/*"
          isLoading={isALoading}
          stats={[
            { label: 'Avg Automation Risk', value: latestRisk?.avg_automation_risk != null ? `${(latestRisk.avg_automation_risk * 100).toFixed(0)}%` : '—' },
            { label: 'Avg Future Safe',     value: latestRisk?.avg_future_safe     != null ? `${(latestRisk.avg_future_safe * 100).toFixed(0)}%`     : '—' },
            { label: 'Safest Career',       value: safestCareer   ? safestCareer.role_name   : '—' },
            { label: 'Most At-Risk Sector', value: riskiestInd    ? riskiestInd.industry_name : '—' },
          ]}
          insights={[
            latestRisk
              ? `Global automation risk index stands at ${((latestRisk.avg_automation_risk ?? 0) * 100).toFixed(0)}% with a future-safe score of ${((latestRisk.avg_future_safe ?? 0) * 100).toFixed(0)}% in 2024.`
              : 'Disruption trend data loading…',
            safestCareer
              ? `${safestCareer.role_name} ranks as the most future-safe career with a ${((safestCareer.avg_future_safe_score ?? 0) * 100).toFixed(0)}% safety score.`
              : 'Career safety data loading…',
            riskiestInd
              ? `${riskiestInd.industry_name} faces the highest disruption pressure with ${((riskiestInd.avg_automation_risk ?? 0) * 100).toFixed(0)}% automation risk and ${riskiestInd.ai_adoption_index.toFixed(2)} AI adoption index.`
              : 'Industry disruption data loading…',
          ]}
        />

      </div>
    </div>
  )
}