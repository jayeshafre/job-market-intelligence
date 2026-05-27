import type { SuggestedPrompt } from '@/hooks/useSuggestedPrompts'
import { Sparkles } from 'lucide-react'

interface Props {
  prompts:  SuggestedPrompt[]
  onSelect: (text: string) => void
  label?:   string
}

export default function SuggestedPrompts({ prompts, onSelect, label = 'Suggested questions' }: Props) {
  return (
    <div className="px-4 pb-4">
      <div className="flex items-center gap-1.5 mb-2.5">
        <Sparkles size={11} className="text-text-muted" />
        <span className="font-mono text-[10px] text-text-muted uppercase tracking-wider">{label}</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {prompts.map((p, i) => (
          <button
            key={i}
            onClick={() => onSelect(p.text)}
            className="text-left px-3 py-2.5 rounded-xl text-[12px] text-text-secondary
                       border border-border hover:border-accent-border hover:text-text-primary
                       hover:bg-base-700 transition-all duration-150 leading-snug group"
          >
            <span className="font-mono text-[9px] text-text-muted group-hover:text-accent-DEFAULT
                             uppercase tracking-wider block mb-1 transition-colors">
              {p.category}
            </span>
            {p.text}
          </button>
        ))}
      </div>
    </div>
  )
}