import clsx from 'clsx'
import type { ChatIntent } from '@/types/ai'

// Maps each intent to a label and colour
const INTENT_CONFIG: Record<ChatIntent, { label: string; color: string; bg: string; border: string }> = {
  salary:        { label: 'Salary',      color: '#4ADE80', bg: 'rgba(74,222,128,0.08)',   border: 'rgba(74,222,128,0.2)'   },
  skills:        { label: 'Skills',      color: '#22D3EE', bg: 'rgba(34,211,238,0.08)',   border: 'rgba(34,211,238,0.2)'   },
  hiring:        { label: 'Hiring',      color: '#818CF8', bg: 'rgba(129,140,248,0.08)',  border: 'rgba(129,140,248,0.2)'  },
  ai_disruption: { label: 'AI Impact',   color: '#F87171', bg: 'rgba(248,113,113,0.08)',  border: 'rgba(248,113,113,0.2)'  },
  forecast:      { label: 'Forecast',    color: '#FBBF24', bg: 'rgba(251,191,36,0.08)',   border: 'rgba(251,191,36,0.2)'   },
  general:       { label: 'General',     color: '#8B949E', bg: 'rgba(139,148,158,0.08)',  border: 'rgba(139,148,158,0.2)'  },
}

interface Props {
  intent: ChatIntent
  className?: string
}

export default function IntentBadge({ intent, className }: Props) {
  const cfg = INTENT_CONFIG[intent] ?? INTENT_CONFIG.general
  return (
    <span
      className={clsx('font-mono text-[9px] uppercase tracking-widest px-1.5 py-0.5 rounded flex-shrink-0', className)}
      style={{ color: cfg.color, background: cfg.bg, border: `1px solid ${cfg.border}` }}
    >
      {cfg.label}
    </span>
  )
}