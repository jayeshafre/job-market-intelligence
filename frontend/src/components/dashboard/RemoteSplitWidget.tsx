import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import type { RemoteSplit } from '@/types/dashboard'
import SectionHeader from '@/components/shared/SectionHeader'

// ─────────────────────────────────────────
// RemoteSplitWidget
//
// Donut chart — remote / hybrid / onsite split
// Data source: GET /workforce/remote-split
// ─────────────────────────────────────────

interface Props {
  data: RemoteSplit
  isLoading?: boolean
}

const COLORS = ['#22D3EE', '#818CF8', '#484F58']
const LABELS = ['Remote', 'Hybrid', 'On-site']

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  return (
    <div
      className="rounded-lg px-3 py-2 text-[12px]"
      style={{ background: '#1C2333', border: '1px solid #21262D' }}
    >
      <span className="text-text-secondary">{payload[0].name}: </span>
      <span className="font-mono font-medium text-text-primary">{payload[0].value}%</span>
    </div>
  )
}

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse">
      <div className="h-4 w-32 bg-base-600 rounded mb-4" />
      <div className="h-32 w-32 rounded-full bg-base-700 mx-auto mb-4" />
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-3 bg-base-600 rounded" />
        ))}
      </div>
    </div>
  )
}

export default function RemoteSplitWidget({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />

  const chartData = [
    { name: 'Remote',  value: data.remote_pct  },
    { name: 'Hybrid',  value: data.hybrid_pct  },
    { name: 'On-site', value: data.onsite_pct  },
  ]

  return (
    <div className="kpi-card page-enter">
      <SectionHeader
        title="Work Mode Split"
        subtitle="Remote · Hybrid · On-site"
      />

      {/* Donut */}
      <ResponsiveContainer width="100%" height={130}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={38}
            outerRadius={58}
            paddingAngle={3}
            dataKey="value"
            strokeWidth={0}
          >
            {chartData.map((_, idx) => (
              <Cell key={idx} fill={COLORS[idx]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex flex-col gap-2 mt-2">
        {chartData.map((item, idx) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ background: COLORS[idx] }}
              />
              <span className="text-[12px] text-text-secondary">{LABELS[idx]}</span>
            </div>
            <span className="font-mono text-[12px] text-text-primary font-medium">
              {item.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}