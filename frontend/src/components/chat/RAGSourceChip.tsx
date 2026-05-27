import type { RetrievedChunk } from '@/types/ai'
import { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react'

interface Props { chunks: RetrievedChunk[] }

export default function RAGSourceChip({ chunks }: Props) {
  const [expanded, setExpanded] = useState(false)
  if (!chunks.length) return null

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(v => !v)}
        className="flex items-center gap-1.5 font-mono text-[10px] text-text-muted hover:text-text-secondary transition-colors"
      >
        <BookOpen size={10} />
        {chunks.length} knowledge source{chunks.length > 1 ? 's' : ''} referenced
        {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>

      {expanded && (
        <div className="mt-2 space-y-1.5">
          {chunks.map((c, i) => (
            <div key={i} className="px-2.5 py-2 rounded-lg text-[11px]"
              style={{ background: 'rgba(34,211,238,0.04)', border: '1px solid rgba(34,211,238,0.1)' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-[9px] text-accent-DEFAULT uppercase tracking-wider">
                  {c.doc_id}
                </span>
                <span className="font-mono text-[9px] text-text-muted">
                  {(c.similarity * 100).toFixed(0)}% match
                </span>
              </div>
              <p className="text-text-secondary leading-relaxed line-clamp-2">{c.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}