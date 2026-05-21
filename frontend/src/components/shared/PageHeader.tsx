import { RefreshCw } from 'lucide-react'

interface PageHeaderProps {
  crumb: string
  title: string
  description: string
  isLoading: boolean
  onRefetch: () => void
}

export default function PageHeader({
  crumb, title, description, isLoading, onRefetch,
}: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-5">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-widest text-text-muted mb-1">
          {crumb}
        </p>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight">{title}</h1>
        <p className="text-[13px] text-text-secondary mt-0.5">{description}</p>
      </div>
      <button
        onClick={onRefetch}
        disabled={isLoading}
        aria-label="Refresh data"
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] text-text-secondary
                   border border-border hover:border-border-light hover:text-text-primary
                   transition-all duration-150 disabled:opacity-40 flex-shrink-0"
      >
        <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} aria-hidden="true" />
        Refresh
      </button>
    </div>
  )
}