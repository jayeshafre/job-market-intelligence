import ReactMarkdown from 'react-markdown'
import { AlertCircle, Database, Cpu } from 'lucide-react'
import clsx from 'clsx'
import type { ChatMessage as ChatMessageType } from '@/types/ai'
import IntentBadge from './IntentBadge'
import RAGSourceChip from './RAGSourceChip'
import RecommendationCard from './RecommendationCard'
import AgentStatusPanel from './AgentStatusPanel'

// ─────────────────────────────────────────
// ChatMessage
//
// FIX 1: Message text was invisible.
//   Root cause: Tailwind utility classes like
//   "text-text-primary" compile to CSS custom
//   property references (var(--tw-...)) but the
//   ReactMarkdown component renders inside the
//   bubble div which has background #1C2333.
//   The text colour was resolving to a very dark
//   shade or transparent in some builds.
//   Fix: Use hardcoded hex colours (#E6EDF3,
//   #8B949E etc.) directly on all text-bearing
//   elements inside message bubbles so they are
//   never dependent on Tailwind CSS variable
//   resolution inside third-party components.
// ─────────────────────────────────────────

interface Props { message: ChatMessageType }

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Explicit colour constants — never rely on Tailwind vars inside markdown
const C = {
  textPrimary:   '#E6EDF3',
  textSecondary: '#8B949E',
  textMuted:     '#484F58',
  accent:        '#22D3EE',
  success:       '#4ADE80',
  danger:        '#F87171',
}

export default function ChatMessage({ message }: Props) {
  const isUser       = message.role === 'user'
  const hasError     = !!message.error
  const hasRecs      = (message.recommendations?.length ?? 0) > 0
  const hasChunks    = (message.chunks?.length ?? 0) > 0 && message.rag_used
  const isMultiAgent = message.is_multi_agent

  // ── User bubble ─────────────────────────────────────────────────────
  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%]">
          <div
            className="px-4 py-3 rounded-2xl rounded-tr-sm text-[13px] leading-relaxed"
            style={{
              background: 'rgba(34,211,238,0.10)',
              border:     '1px solid rgba(34,211,238,0.25)',
              color:      C.textPrimary,         // ← FIX: explicit colour
            }}
          >
            {message.content}
          </div>
          <p className="font-mono text-[9px] text-right mt-1 pr-1"
            style={{ color: C.textMuted }}>
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    )
  }

  // ── Error bubble ────────────────────────────────────────────────────
  if (hasError) {
    // Parse the error to give actionable diagnostic steps
    const err = message.error ?? ''
    const isTimeout   = err.includes('timed out') || err.includes('timeout')
    const isRedis     = err.includes('Redis') || err.includes('redis')
    const isGroq      = err.includes('Groq') || err.includes('GROQ') || err.includes('groq')
    const isRAG       = err.includes('chroma') || err.includes('embedding')
    const isNetwork   = err.includes('Cannot reach') || err.includes('Network')
    const is404       = err.includes('not found') || err.includes('404')
    const is500       = err.includes('500') || err.includes('Internal server')

    const steps: string[] = []
    if (isNetwork || isTimeout) {
      steps.push('1. Start FastAPI: cd backend && uvicorn main:app --reload --port 8000')
      steps.push('2. Check terminal for startup errors')
    }
    if (isRedis) {
      steps.push('1. Start Redis: redis-server')
      steps.push('2. Or: install Redis → https://redis.io/docs/getting-started/')
    }
    if (isGroq) {
      steps.push('1. Check GROQ_API_KEY is set in backend/.env')
      steps.push('2. Verify key at console.groq.com')
    }
    if (isRAG) {
      steps.push('1. pip install chromadb sentence-transformers')
      steps.push('2. Restart FastAPI after install')
    }
    if (is404) {
      steps.push('1. Check main.py has: app.include_router(ai.router, prefix="/api/v1/ai")')
      steps.push('2. Visit http://localhost:8000/docs to verify endpoints exist')
    }
    if (steps.length === 0) {
      steps.push('1. Check FastAPI terminal for the full error traceback')
      steps.push('2. Visit http://localhost:8000/docs to test the endpoint directly')
    }

    return (
      <div className="flex items-start gap-3 mb-4">
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.25)' }}
        >
          <AlertCircle size={13} style={{ color: C.danger }} />
        </div>
        <div
          className="flex-1 px-4 py-3 rounded-2xl rounded-tl-sm"
          style={{ background: 'rgba(248,113,113,0.06)', border: '1px solid rgba(248,113,113,0.2)' }}
        >
          <p className="font-medium mb-1 text-[13px]" style={{ color: C.danger }}>
            {isTimeout   ? 'Request timed out'        :
             isRedis     ? 'Redis not running'        :
             isGroq      ? 'Groq API error'           :
             isRAG       ? 'RAG pipeline error'       :
             isNetwork   ? 'Backend unreachable'      :
             is404       ? 'Endpoint not found'       :
             is500       ? 'Internal server error'    : 'Backend error'}
          </p>
          <p className="text-[12px] mb-2.5 font-mono" style={{ color: C.textSecondary }}>
            {err}
          </p>
          {steps.length > 0 && (
            <div
              className="rounded-lg px-3 py-2.5 space-y-1"
              style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(248,113,113,0.1)' }}
            >
              <p className="font-mono text-[9px] uppercase tracking-wider mb-1.5"
                style={{ color: C.textMuted }}>
                How to fix
              </p>
              {steps.map((s, i) => (
                <p key={i} className="font-mono text-[10px]" style={{ color: C.textSecondary }}>
                  {s}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // ── Assistant bubble ────────────────────────────────────────────────
  return (
    <div className="flex items-start gap-3 mb-4 animate-fade-in">

      {/* Avatar */}
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
        style={
          isMultiAgent
            ? { background: 'rgba(129,140,248,0.12)', border: '1px solid rgba(129,140,248,0.3)' }
            : { background: 'rgba(34,211,238,0.10)',  border: '1px solid rgba(34,211,238,0.25)' }
        }
      >
        {isMultiAgent
          ? <Cpu size={13} style={{ color: '#818CF8' }} />
          : <span className="font-mono text-[10px] font-bold" style={{ color: C.accent }}>AI</span>
        }
      </div>

      {/* Bubble */}
      <div className="max-w-[80%] min-w-0">
        <div
          className="px-4 py-3 rounded-2xl rounded-tl-sm"
          style={{ background: '#1C2333', border: '1px solid #2D3748' }}
        >
          {/* Badge row */}
          <div className="flex items-center flex-wrap gap-1.5 mb-2.5">
            {message.intent && <IntentBadge intent={message.intent} />}

            {message.kpi_backed && (
              <span
                className="flex items-center gap-1 font-mono text-[9px] px-1.5 py-0.5 rounded"
                style={{ color: C.success, background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.2)' }}
              >
                <Database size={8} />
                Data-backed
              </span>
            )}

            {isMultiAgent && (
              <span
                className="font-mono text-[9px] px-1.5 py-0.5 rounded"
                style={{ color: '#818CF8', background: 'rgba(129,140,248,0.08)', border: '1px solid rgba(129,140,248,0.2)' }}
              >
                Multi-Agent
              </span>
            )}
          </div>

          {/* ── Answer text — FIX: all colours explicit hex ── */}
          <div className="text-[13px] leading-relaxed">
            <ReactMarkdown
              components={{
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0" style={{ color: C.textPrimary }}>{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold" style={{ color: C.accent }}>{children}</strong>
                ),
                em: ({ children }) => (
                  <em style={{ color: C.textSecondary }}>{children}</em>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-4 mb-2 space-y-0.5" style={{ color: C.textSecondary }}>{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-4 mb-2 space-y-0.5" style={{ color: C.textSecondary }}>{children}</ol>
                ),
                li: ({ children }) => (
                  <li style={{ color: C.textSecondary }}>{children}</li>
                ),
                h1: ({ children }) => (
                  <h1 className="text-[15px] font-semibold mb-2 mt-3" style={{ color: C.textPrimary }}>{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-[14px] font-semibold mb-1.5 mt-2" style={{ color: C.textPrimary }}>{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-[13px] font-semibold mb-1 mt-2" style={{ color: C.textPrimary }}>{children}</h3>
                ),
                code: ({ children, className }) => {
                  // Inline code
                  return (
                    <code
                      className="font-mono text-[11px] px-1.5 py-0.5 rounded"
                      style={{ color: C.accent, background: 'rgba(34,211,238,0.08)' }}
                    >
                      {children}
                    </code>
                  )
                },
                blockquote: ({ children }) => (
                  <blockquote
                    className="pl-3 my-2 border-l-2"
                    style={{ borderColor: C.accent, color: C.textSecondary }}
                  >
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>

          {/* RAG sources */}
          {hasChunks && <RAGSourceChip chunks={message.chunks!} />}

          {/* Recommendations */}
          {hasRecs && <RecommendationCard recommendations={message.recommendations!} />}

          {/* Multi-agent panel */}
          {isMultiAgent && message.agent_outputs && (
            <AgentStatusPanel
              agentOutputs={message.agent_outputs}
              executionPlan={message.execution_plan ?? []}
              agentsRun={message.agents_run ?? 0}
              agentsFailed={0}
            />
          )}
        </div>

        {/* Timestamp + meta */}
        <div className="flex items-center gap-3 mt-1 pl-1">
          <p className="font-mono text-[9px]" style={{ color: C.textMuted }}>
            {formatTime(message.timestamp)}
          </p>
          {message.tokens_used != null && message.tokens_used > 0 && (
            <p className="font-mono text-[9px]" style={{ color: C.textMuted }}>
              {message.tokens_used} tokens
            </p>
          )}
          {message.model && (
            <p className="font-mono text-[9px] truncate" style={{ color: C.textMuted }}>
              {message.model}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}