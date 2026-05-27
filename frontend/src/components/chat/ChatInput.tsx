import { useState, useRef, useEffect } from 'react'
import { Send, Cpu, Zap } from 'lucide-react'
import clsx from 'clsx'
import type { ChatMode } from '@/types/ai'

// ─────────────────────────────────────────
// ChatInput
//
// Auto-resizing textarea + send button.
// Supports Enter to send, Shift+Enter for newline.
// Shows mode toggle between standard (v6) and
// multi-agent (v7).
// ─────────────────────────────────────────

interface Props {
  onSend:      (text: string) => void
  isLoading:   boolean
  mode:        ChatMode
  onModeChange:(m: ChatMode) => void
  disabled?:   boolean
}

export default function ChatInput({ onSend, isLoading, mode, onModeChange, disabled }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`
  }, [value])

  function handleSend() {
    if (!value.trim() || isLoading || disabled) return
    onSend(value.trim())
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = value.trim().length >= 5 && !isLoading && !disabled

  return (
    <div className="px-4 pb-4 pt-2">
      {/* Mode toggle */}
      <div className="flex items-center gap-2 mb-2">
        <span className="font-mono text-[10px] text-text-muted uppercase tracking-wider">Mode:</span>
        <div className="flex gap-1 p-0.5 rounded-md bg-base-700">
          <button
            onClick={() => onModeChange('standard')}
            className={clsx(
              'flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium transition-all duration-150',
              mode === 'standard'
                ? 'bg-base-800 text-text-primary border border-border'
                : 'text-text-muted hover:text-text-secondary'
            )}
          >
            <Zap size={10} />
            Standard
          </button>
          <button
            onClick={() => onModeChange('multi-agent')}
            className={clsx(
              'flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium transition-all duration-150',
              mode === 'multi-agent'
                ? 'bg-base-800 text-info border border-border'
                : 'text-text-muted hover:text-text-secondary'
            )}
          >
            <Cpu size={10} />
            Multi-Agent
          </button>
        </div>
        {mode === 'multi-agent' && (
          <span className="font-mono text-[9px] text-info">
            Activates all 5 specialist agents
          </span>
        )}
      </div>

      {/* Input row */}
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === 'multi-agent'
                ? 'Ask for deep analysis — all agents will respond…'
                : 'Ask about jobs, salaries, skills, or AI disruption…'
            }
            disabled={isLoading || disabled}
            rows={1}
            className={clsx(
              'w-full resize-none rounded-xl px-4 py-3 pr-12 text-[13px] font-sans',
              'text-text-primary placeholder:text-text-muted',
              'bg-base-700 border border-border',
              'outline-none focus:border-accent-border',
              'transition-colors duration-150',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'max-h-36 overflow-y-auto',
            )}
            style={{ lineHeight: '1.5' }}
          />
          <span className="absolute right-3 bottom-3 font-mono text-[9px] text-text-muted">
            {value.length}/500
          </span>
        </div>

        <button
          onClick={handleSend}
          disabled={!canSend}
          aria-label="Send message"
          className={clsx(
            'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
            'transition-all duration-150',
            canSend
              ? 'bg-accent-DEFAULT text-base-900 hover:bg-cyan-300 shadow-glow'
              : 'bg-base-700 text-text-muted cursor-not-allowed'
          )}
        >
          <Send size={16} aria-hidden="true" />
        </button>
      </div>

      <p className="font-mono text-[9px] text-text-muted text-center mt-2">
        Enter to send · Shift+Enter for new line · Min 5 characters
      </p>
    </div>
  )
}