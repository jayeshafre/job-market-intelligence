import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'
import type { GrowingSkill } from '@/types/skills'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: GrowingSkill[]; isLoading?: boolean }

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as GrowingSkill
  return (
    <div className="rounded-lg px-3 py-2.5 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}>
      <div className="flex items-center gap-2 mb-1">
        <p className="text-text-primary font-medium">{d.skill_name}</p>
        {d.is_ai_related && (
          <span className="font-mono text-[9px] px-1.5 py-0.5 rounded"
            style={{ background: 'rgba(34,211,238,0.1)', border: '1px solid rgba(34,211,238,0.2)', color: '#22D3EE' }}>
            AI
          </span>
        )}
      </div>
      <p className="font-mono text-text-muted text-[11px]">{d.skill_category}</p>
      <div className="flex gap-3 mt-1">
        <span className="font-mono text-success text-[11px]">+{d.growth_pct?.toFixed(1)}% growth</span>
        {d.avg_demand_score && <span className="font-mono text-accent-DEFAULT text-[11px]">{d.avg_demand_score.toFixed(1)} demand</span>}
      </div>
    </div>
  )
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-40 bg-base-600 rounded mb-2" /><div className="h-64 bg-base-700 rounded-lg" /></div>
}

export default function TopGrowingSkillsChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Fastest Growing Skills" subtitle="YoY demand growth % · 2024" badge="TOP 10" />
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 40, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" horizontal={false} />
          <XAxis type="number" tickFormatter={v => `${v}%`} tick={{ fill: '#484F58', fontSize: 10, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="skill_name" tick={{ fill: '#8B949E', fontSize: 11, fontFamily: 'DM Sans' }} axisLine={false} tickLine={false} width={130} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34,211,238,0.04)' }} />
          <Bar dataKey="growth_pct" radius={[0, 3, 3, 0]} maxBarSize={16}>
            {data.map((d, idx) => (
              <Cell key={idx}
                fill={d.is_ai_related ? '#22D3EE' : `rgba(129,140,248,${0.8 - idx * 0.05})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {/* Legend */}
      <div className="flex items-center gap-4 mt-1">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-accent-DEFAULT" />
          <span className="font-mono text-[10px] text-text-muted">AI-related skill</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-info" />
          <span className="font-mono text-[10px] text-text-muted">General skill</span>
        </div>
      </div>
    </div>
  )
}