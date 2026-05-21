import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import type { RemoteBreakdown } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// RemoteSplitWidget
//
// AUDIT FIX: Was typed to RemoteSplit (invented type
// with hybrid_pct — doesn't exist in backend).
//
// Real backend RemoteBreakdown has:
//   total_postings   number
//   remote_postings  number
//   onsite_postings  number
//   remote_pct       number
//
// There is NO hybrid data from the backend.
// We now show: Remote vs On-site (2 slices).
// Hybrid is computed from the gap if we want it,
// but only from real fields — not invented ratios.
//
// Data source: GET /api/v1/workforce/remote-stats
// ─────────────────────────────────────────

interface Props {
  data: RemoteBreakdown
  isLoading?: boolean
}

const COLORS = ['#22D3EE', '#484F58']
const LABELS = ['Remote', 'On-site']

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg px-3 py-2 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}>
      <span className="text-text-secondary">{payload[0].name}: </span>
      <span className="font-mono font-medium text-text-primary">{payload[0].value.toFixed(1)}%</span>
    </div>
  )
}

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse">
      <div className="h-4 w-32 bg-base-600 rounded mb-4" />
      <div className="h-32 w-32 rounded-full bg-base-700 mx-auto mb-4" />
      <div className="space-y-2">
        {[...Array(2)].map((_, i) => <div key={i} className="h-3 bg-base-600 rounded" />)}
      </div>
    </div>
  )
}

export default function RemoteSplitWidget({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  // AUDIT FIX: compute real percentages from real fields
  const total        = data.total_postings
  const remotePct    = data.remote_pct                                          // direct from API
  const onsitePct    = total > 0
    ? parseFloat(((data.onsite_postings / total) * 100).toFixed(1))
    : parseFloat((100 - remotePct).toFixed(1))

  const chartData = [
    { name: 'Remote',  value: remotePct  },
    { name: 'On-site', value: onsitePct  },
  ]

  function fmtCount(n: number) {
    return n >= 1_000 ? `${(n / 1_000).toFixed(0)}K` : String(n)
  }

  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Work Mode Split" subtitle="Remote vs On-site · 2024" />

      <ResponsiveContainer width="100%" height={130}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={38} outerRadius={58}
            paddingAngle={3} dataKey="value" strokeWidth={0}>
            {chartData.map((_, idx) => <Cell key={idx} fill={COLORS[idx]} />)}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="flex flex-col gap-2 mt-2">
        {chartData.map((item, idx) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: COLORS[idx] }} />
              <span className="text-[12px] text-text-secondary">{LABELS[idx]}</span>
            </div>
            <div className="flex items-center gap-2">
              {/* Show real absolute count alongside percentage */}
              <span className="font-mono text-[10px] text-text-muted">
                {idx === 0 ? fmtCount(data.remote_postings) : fmtCount(data.onsite_postings)}
              </span>
              <span className="font-mono text-[12px] text-text-primary font-medium">
                {item.value.toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
        {/* Total postings context */}
        <div className="pt-2 border-t border-border mt-1">
          <span className="font-mono text-[10px] text-text-muted">
            Total: {fmtCount(data.total_postings)} postings
          </span>
        </div>
      </div>
    </div>
  )
}