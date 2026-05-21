import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'
import type { TopPayingRole } from '@/types/salary'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: TopPayingRole[]; isLoading?: boolean }

function fmt(v: number) { return `$${(v / 1000).toFixed(0)}K` }

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as TopPayingRole
  return (
    <div className="rounded-lg px-3 py-2.5 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}>
      <p className="text-text-primary font-medium mb-1">{d.role_name}</p>
      <p className="font-mono text-text-muted text-[11px]">{d.seniority_level} · {d.role_category}</p>
      <p className="font-mono text-accent-DEFAULT mt-1 font-medium">{fmt(d.avg_salary_usd)}</p>
    </div>
  )
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-36 bg-base-600 rounded mb-2" /><div className="h-56 bg-base-700 rounded-lg" /></div>
}

export default function TopPayingRolesChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  // Shorten long role names for axis
  const chartData = data.map(d => ({
    ...d,
    short_name: d.role_name.length > 18 ? d.role_name.slice(0, 16) + '…' : d.role_name,
  }))

  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Top Paying Roles" subtitle="Average salary (USD) · 2024" />
      <ResponsiveContainer width="100%" height={230}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" horizontal={false} />
          <XAxis type="number" tickFormatter={fmt} tick={{ fill: '#484F58', fontSize: 10, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="short_name" tick={{ fill: '#8B949E', fontSize: 11, fontFamily: 'DM Sans' }} axisLine={false} tickLine={false} width={120} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34,211,238,0.04)' }} />
          <Bar dataKey="avg_salary_usd" radius={[0, 3, 3, 0]} maxBarSize={18}>
            {chartData.map((_, idx) => (
              <Cell key={idx} fill={idx === 0 ? '#22D3EE' : `rgba(34,211,238,${0.75 - idx * 0.1})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}