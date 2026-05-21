import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'
import type { SkillCategorySummary } from '@/types/skills'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: SkillCategorySummary[]; isLoading?: boolean }

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as SkillCategorySummary
  return (
    <div className="rounded-lg px-3 py-2.5 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}>
      <p className="text-text-primary font-medium mb-1">{d.skill_category}</p>
      <div className="space-y-0.5">
        <p className="font-mono text-[11px] text-text-muted">{d.skill_count} total skills</p>
        <p className="font-mono text-[11px] text-accent-DEFAULT">{d.ai_skill_count} AI skills</p>
        <p className="font-mono text-[11px] text-success">+{d.avg_growth_pct?.toFixed(1)}% avg growth</p>
      </div>
    </div>
  )
}

const CATEGORY_COLORS: Record<string, string> = {
  'AI/ML':        '#22D3EE',
  'Cloud/DevOps': '#818CF8',
  'Data':         '#34D399',
  'Programming':  '#F97316',
  'Security':     '#F87171',
  'Databases':    '#FBBF24',
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-36 bg-base-600 rounded mb-2" /><div className="h-52 bg-base-700 rounded-lg" /></div>
}

export default function SkillCategoryChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Growth by Skill Category" subtitle="Average YoY demand growth % per category" />
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" vertical={false} />
          <XAxis dataKey="skill_category" tick={{ fill: '#8B949E', fontSize: 10, fontFamily: 'DM Sans' }} axisLine={false} tickLine={false} angle={-20} textAnchor="end" interval={0} />
          <YAxis tickFormatter={v => `${v}%`} tick={{ fill: '#484F58', fontSize: 10, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} width={36} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="avg_growth_pct" radius={[3, 3, 0, 0]} maxBarSize={40}>
            {data.map((d) => (
              <Cell key={d.skill_category} fill={CATEGORY_COLORS[d.skill_category] ?? '#484F58'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}