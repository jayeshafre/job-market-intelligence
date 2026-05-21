import { Brain, TrendingUp, Sparkles, Layers } from 'lucide-react'
import { useSkills } from '@/hooks/useSkills'
import PageHeader from '@/components/shared/PageHeader'
import KpiCard, { fmtPct } from '@/components/dashboard/KpiCard'
import TopGrowingSkillsChart from '@/components/skills/TopGrowingSkillsChart'
import SkillCategoryChart from '@/components/skills/SkillCategoryChart'
import SectionHeader from '@/components/shared/SectionHeader'

export default function SkillIntelligence() {
  const { data, status, error, refetch } = useSkills()
  const isLoading = status === 'idle' || status === 'loading'

  const topSkill      = data?.topGrowing[0]
  const topAiSkill    = data?.aiSkills[0]
  const totalCategories = data?.byCategory.length ?? 0
  const aiSkillCount  = data?.byCategory.reduce((s, c) => s + c.ai_skill_count, 0) ?? 0

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="intelligence"
        title="Skill Intelligence"
        description="Fastest growing skills, AI/ML demand, technology adoption trends"
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
        <KpiCard label="Fastest Growing"  value={topSkill && !isLoading ? topSkill.skill_name : '—'}        delta={topSkill ? `+${fmtPct(topSkill.growth_pct ?? 0)} YoY` : undefined} trend="up"      icon={TrendingUp} isLoading={isLoading} />
        <KpiCard label="Top AI Skill"     value={topAiSkill && !isLoading ? topAiSkill.skill_name : '—'}    delta={topAiSkill?.avg_demand_score ? `${topAiSkill.avg_demand_score.toFixed(1)} demand` : undefined} trend="up" icon={Sparkles} isLoading={isLoading} />
        <KpiCard label="Skill Categories" value={isLoading ? '—' : String(totalCategories)}                 delta="tracked categories"          trend="neutral" icon={Layers}    isLoading={isLoading} />
        <KpiCard label="AI-Related Skills" value={isLoading ? '—' : String(aiSkillCount)}                  delta="AI/ML skills tracked"         trend="up"      icon={Brain}     isLoading={isLoading} />
      </div>

      {/* Top growing + by category */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <TopGrowingSkillsChart data={data?.topGrowing ?? []} isLoading={isLoading} />
        <SkillCategoryChart    data={data?.byCategory ?? []} isLoading={isLoading} />
      </div>

      {/* AI skills table */}
      <div className="kpi-card page-enter">
        <SectionHeader title="AI & ML Skill Demand" subtitle="AI-related skills ranked by avg demand score · 2024" badge="AI SKILLS" />
        <div className="grid grid-cols-12 gap-2 px-2 mb-1">
          {['Skill', 'Category', 'Demand Score', 'Growth', 'Mentions'].map((h, i) => (
            <span key={h} className={`font-mono text-[10px] text-text-muted uppercase tracking-wider
              ${i === 0 ? 'col-span-3' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-2 text-right' : i === 3 ? 'col-span-2 text-right' : 'col-span-2 text-right'}`}>{h}</span>
          ))}
        </div>
        <div className="space-y-0.5">
          {(isLoading ? Array(6).fill(null) : (data?.aiSkills ?? [])).map((s, i) =>
            isLoading ? (
              <div key={i} className="h-9 bg-base-700 rounded-lg animate-pulse" />
            ) : (
              <div key={s.skill_name} className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                <div className="col-span-3 flex items-center gap-2 min-w-0">
                  <span className="text-[12px] text-text-primary truncate">{s.skill_name}</span>
                </div>
                <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{s.skill_category}</span>
                <span className="col-span-2 font-mono text-[12px] text-accent-DEFAULT font-medium text-right">
                  {s.avg_demand_score?.toFixed(1) ?? '—'}
                </span>
                <span className="col-span-2 font-mono text-[11px] text-success text-right">
                  {s.avg_growth_pct != null ? `+${s.avg_growth_pct.toFixed(1)}%` : '—'}
                </span>
                <span className="col-span-2 font-mono text-[11px] text-text-secondary text-right">
                  {s.total_mentions != null ? (s.total_mentions >= 1000 ? `${(s.total_mentions / 1000).toFixed(1)}K` : s.total_mentions) : '—'}
                </span>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  )
}