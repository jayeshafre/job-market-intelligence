import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import type { DisruptionTrend } from '@/types/aiImpact'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: DisruptionTrend[]; isLoading?: boolean }

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg px-3 py-2.5 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}>
      <p className="font-mono text-text-muted mb-1.5">{label}</p>
      {payload.map((e: any) => (
        <div key={e.name} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full" style={{ background: e.color }} />
          <span className="text-text-secondary">{e.name}:</span>
          <span className="font-mono font-medium text-text-primary">
            {(e.value * 100).toFixed(0)}%
          </span>
        </div>
      ))}
    </div>
  )
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-44 bg-base-600 rounded mb-2" /><div className="h-56 bg-base-700 rounded-lg" /></div>
}

export default function DisruptionTrendChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="AI Disruption Trends" subtitle="Global automation risk vs future-safe score · 2018–2024" />
      <ResponsiveContainer width="100%" height={230}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={v => `${(v * 100).toFixed(0)}%`} tick={{ fill: '#484F58', fontSize: 10, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} width={38} domain={[0, 1]} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#30363D', strokeWidth: 1 }} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: '#8B949E', paddingTop: '12px' }} />
          <Line type="monotone" dataKey="avg_automation_risk" name="Automation Risk" stroke="#F87171" strokeWidth={2} dot={{ fill: '#F87171', r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="avg_future_safe"     name="Future Safe"     stroke="#4ADE80" strokeWidth={2} dot={{ fill: '#4ADE80', r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="avg_ai_replacement"  name="AI Replacement"  stroke="#F97316" strokeWidth={2} strokeDasharray="4 3" dot={false} activeDot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}