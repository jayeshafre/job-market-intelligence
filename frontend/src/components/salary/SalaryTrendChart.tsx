import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import type { SalaryTrendPoint } from '@/types/salary'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: SalaryTrendPoint[]; isLoading?: boolean }

function fmt(v: number) { return `$${(v / 1000).toFixed(0)}K` }

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
          <span className="font-mono font-medium text-text-primary">{fmt(e.value)}</span>
        </div>
      ))}
      {payload[0]?.payload?.salary_growth_pct != null && (
        <p className="font-mono text-[10px] text-success mt-1.5">
          YoY Growth: +{payload[0].payload.salary_growth_pct.toFixed(1)}%
        </p>
      )}
    </div>
  )
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-40 bg-base-600 rounded mb-2" /><div className="h-56 bg-base-700 rounded-lg" /></div>
}

export default function SalaryTrendChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Global Salary Trend" subtitle="Avg & Median salary (USD) · 2018–2024" />
      <ResponsiveContainer width="100%" height={230}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={fmt} tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} width={46} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#30363D', strokeWidth: 1 }} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: '#8B949E', paddingTop: '12px' }} />
          <Line type="monotone" dataKey="avg_salary_usd"    name="Avg Salary"    stroke="#22D3EE" strokeWidth={2} dot={{ fill: '#22D3EE', r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="median_salary_usd" name="Median Salary" stroke="#818CF8" strokeWidth={2} strokeDasharray="5 3" dot={{ fill: '#818CF8', r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}