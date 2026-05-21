import type { TopRole } from '@/types/workforce'
import SectionHeader from '@/components/shared/SectionHeader'
import clsx from 'clsx'

interface Props { data: TopRole[]; isLoading?: boolean }

function Skeleton() {
  return (
    <div className="kpi-card animate-pulse space-y-2">
      <div className="h-4 w-32 bg-base-600 rounded mb-3" />
      {[...Array(6)].map((_, i) => <div key={i} className="h-9 bg-base-700 rounded-lg" />)}
    </div>
  )
}

export default function TopRolesTable({ data, isLoading = false }: Props) {
  if (isLoading) return <Skeleton />
  return (
    <div className="kpi-card page-enter">
      <SectionHeader title="Top Roles by Volume" subtitle="Most in-demand positions · 2024" />
      {/* Header */}
      <div className="grid grid-cols-12 gap-2 px-2 mb-1">
        {['Role', 'Category', 'Level', 'Postings', 'Remote'].map((h, i) => (
          <span key={h} className={clsx('font-mono text-[10px] text-text-muted uppercase tracking-wider',
            i === 0 ? 'col-span-4' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-2' : i === 3 ? 'col-span-2 text-right' : 'col-span-1 text-center'
          )}>{h}</span>
        ))}
      </div>
      <div className="space-y-0.5">
        {data.map((r, idx) => (
          <div key={r.role_name}
            className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
            <div className="col-span-4 flex items-center gap-2 min-w-0">
              <span className="font-mono text-[10px] text-text-muted w-4 flex-shrink-0">{idx + 1}</span>
              <span className="text-[12px] text-text-primary truncate">{r.role_name}</span>
            </div>
            <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{r.role_category}</span>
            <span className="col-span-2 font-mono text-[10px] text-text-muted truncate">{r.seniority_level}</span>
            <span className="col-span-2 font-mono text-[11px] text-accent-DEFAULT text-right">
              {r.total_postings >= 1000 ? `${(r.total_postings / 1000).toFixed(1)}K` : r.total_postings}
            </span>
            <span className="col-span-1 text-center text-[11px]">
              {r.is_remote_eligible ? '✓' : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}