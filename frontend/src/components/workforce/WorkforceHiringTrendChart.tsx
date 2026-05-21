import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import type { HiringTrendPoint } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'

interface Props { data: HiringTrendPoint[]; isLoading?: boolean }

function fmt(v: number) {
  return v >= 1_000 ? `${(v / 1_000).toFixed(0)}K` : String(v)
}

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
    </div>
  )
}

function Skeleton() {
  return <div className="kpi-card animate-pulse"><div className="h-4 w-40 bg-base-600 rounded mb-2" /><div className="h-56 bg-base-700 rounded-lg" /></div>
}

export default function WorkforceHiringTrendChart({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Hiring Volume Over Time" subtitle="Total vs Remote postings · 2018–2024" />
      <ResponsiveContainer width="100%" height={230}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#22D3EE" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#22D3EE" stopOpacity={0}    />
            </linearGradient>
            <linearGradient id="remoteGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#818CF8" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#818CF8" stopOpacity={0}    />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={fmt} tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} width={42} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#30363D', strokeWidth: 1 }} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: '#8B949E', paddingTop: '12px' }} />
          <Area type="monotone" dataKey="total_postings"  name="Total"  stroke="#22D3EE" strokeWidth={2} fill="url(#totalGrad)"  dot={false} activeDot={{ r: 4 }} />
          <Area type="monotone" dataKey="remote_postings" name="Remote" stroke="#818CF8" strokeWidth={2} fill="url(#remoteGrad)" dot={false} activeDot={{ r: 4 }} strokeDasharray="5 3" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}