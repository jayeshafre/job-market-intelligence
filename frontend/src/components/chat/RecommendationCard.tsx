import type { Recommendation } from '@/types/ai'
import { TrendingUp, Brain, Globe, Factory, ArrowRight } from 'lucide-react'

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  role:          ArrowRight,
  skill:         Brain,
  country:       Globe,
  industry:      Factory,
  career_pivot:  TrendingUp,
}

const PRIORITY_STYLES: Record<string, { color: string; bg: string; border: string }> = {
  high:   { color: '#F87171', bg: 'rgba(248,113,113,0.08)', border: 'rgba(248,113,113,0.2)' },
  medium: { color: '#FBBF24', bg: 'rgba(251,191,36,0.08)',  border: 'rgba(251,191,36,0.2)'  },
  low:    { color: '#4ADE80', bg: 'rgba(74,222,128,0.08)',  border: 'rgba(74,222,128,0.2)'  },
}

interface Props { recommendations: Recommendation[] }

export default function RecommendationCard({ recommendations }: Props) {
  if (!recommendations.length) return null

  return (
    <div className="mt-3 space-y-2">
      <p className="font-mono text-[9px] uppercase tracking-widest text-text-muted mb-1.5">
        AI Recommendations
      </p>
      {recommendations.map((rec, i) => {
        const Icon     = CATEGORY_ICONS[rec.category] ?? ArrowRight
        const priority = PRIORITY_STYLES[rec.priority] ?? PRIORITY_STYLES.low

        return (
          <div key={i} className="rounded-xl p-3"
            style={{ background: '#1C2333', border: '1px solid #21262D' }}>
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-2 min-w-0">
                <Icon size={13} className="text-accent-DEFAULT flex-shrink-0" />
                <p className="text-[12px] font-medium text-text-primary truncate">{rec.title}</p>
              </div>
              <span className="font-mono text-[9px] px-1.5 py-0.5 rounded flex-shrink-0 uppercase tracking-wider"
                style={priority}>
                {rec.priority}
              </span>
            </div>
            <p className="text-[11px] text-text-secondary leading-relaxed mb-1.5">{rec.rationale}</p>
            {rec.estimated_impact && (
              <span className="font-mono text-[10px] text-success">
                Impact: {rec.estimated_impact}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}