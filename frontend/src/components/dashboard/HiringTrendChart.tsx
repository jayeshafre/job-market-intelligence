import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import type { HiringTrendPoint } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// HiringTrendChart
//
// AUDIT FIX: dataKey was "job_postings" —
// real backend field is "total_postings".
// Fixed to match workforce.py schema exactly.
//
// Data source: GET /api/v1/workforce/hiring-trends
// Fields used: year, total_postings, remote_postings
// ─────────────────────────────────────────

interface Props {
  data: HiringTrendPoint[]
  isLoading?: boolean
}

function fmtYAxis(value: number) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000)     return `${(value / 1_000).toFixed(0)}K`
  return String(value)
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg px-3 py-2.5 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D', boxShadow: '0 4px 16px rgba(0,0,0,0.4)' }}>
      <p className="font-mono text-text-muted mb-1.5">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: entry.color }} />
          <span className="text-text-secondary">{entry.name}:</span>
          <span className="font-mono font-medium text-text-primary">{fmtYAxis(entry.value)}</span>
        </div>
      ))}
    </div>
  )
}

function ChartSkeleton() {
  return (
    <div className="kpi-card animate-pulse">
      <div className="h-4 w-40 bg-base-600 rounded mb-1" />
      <div className="h-3 w-24 bg-base-600 rounded mb-6" />
      <div className="h-52 bg-base-700 rounded-lg" />
    </div>
  )
}

export default function HiringTrendChart({ data, isLoading = false }: Props) {
  if (isLoading) return <ChartSkeleton />

  return (
    <div className="kpi-card page-enter">
      <SectionHeader
        title="Global Hiring Trend"
        subtitle="Total vs. Remote job postings · 2018–2024"
        badge="WORKFORCE"
      />
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262D" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={fmtYAxis} tick={{ fill: '#484F58', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} width={42} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#30363D', strokeWidth: 1 }} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: '#8B949E', paddingTop: '12px' }} />

          {/* AUDIT FIX: was "job_postings" — real field is "total_postings" */}
          <Line type="monotone" dataKey="total_postings"  name="Total Postings"  stroke="#22D3EE" strokeWidth={2} dot={{ fill: '#22D3EE', r: 3, strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
          <Line type="monotone" dataKey="remote_postings" name="Remote Postings" stroke="#818CF8" strokeWidth={2} strokeDasharray="5 3" dot={{ fill: '#818CF8', r: 3, strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}