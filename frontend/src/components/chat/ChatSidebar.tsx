import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  MessageSquareText, History, Bookmark, Settings2, Database,
  Plus, Trash2, Clock, ChevronRight, X, Zap, Cpu,
  BookOpen, Globe, Brain, TrendingUp, ShieldCheck,
} from 'lucide-react'
import clsx from 'clsx'
import type { SessionSummary, SavedPrompt } from '@/hooks/useChatHistory'
import type { ChatMode } from '@/types/ai'

// ─────────────────────────────────────────
// ChatSidebar
//
// Four panels accessed via tab icons:
//   chat     — active session info + new chat
//   history  — past session list (localStorage)
//   saved    — saved prompts library
//   settings — model settings + data context
//
// Designed to sit to the LEFT of ChatAssistant
// inside the /chat route layout.
//
// Props:
//   onNewChat        — clears active session
//   onLoadPrompt     — inserts text into chat input
//   sessions         — from useChatHistory
//   savedPrompts     — from useChatHistory
//   onDeleteSession  — remove from history
//   onClearHistory   — wipe all history
//   onDeletePrompt   — remove saved prompt
//   sessionId        — active session id (string | null)
//   turnCount        — active session turn count
//   mode / onModeChange — chat mode toggle
// ─────────────────────────────────────────

type SidebarTab = 'chat' | 'history' | 'saved' | 'settings'

const INTENT_COLORS: Record<string, string> = {
  salary:        '#4ADE80',
  skills:        '#22D3EE',
  hiring:        '#818CF8',
  ai_disruption: '#F87171',
  forecast:      '#FBBF24',
  general:       '#8B949E',
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins  = Math.floor(diff / 60_000)
  const hours = Math.floor(diff / 3_600_000)
  const days  = Math.floor(diff / 86_400_000)
  if (mins < 1)   return 'just now'
  if (mins < 60)  return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

// ── Tab definitions ────────────────────────────────────────────────

const TABS: { id: SidebarTab; icon: React.ElementType; label: string }[] = [
  { id: 'chat',     icon: MessageSquareText, label: 'Chat'     },
  { id: 'history',  icon: History,           label: 'History'  },
  { id: 'saved',    icon: Bookmark,          label: 'Saved'    },
  { id: 'settings', icon: Settings2,         label: 'Settings' },
]

// ── Saved prompts categorized by intent ───────────────────────────

const PRESET_PROMPTS = [
  { text: 'Which skills are growing fastest in 2024?',               category: 'Skills'    },
  { text: 'Which jobs are safest from AI automation?',               category: 'AI Impact' },
  { text: 'Which countries pay the highest salaries?',               category: 'Salary'    },
  { text: 'What are the biggest workforce trends expected in 2025?', category: 'Forecast'  },
  { text: 'Which industries are hiring the most right now?',         category: 'Hiring'    },
  { text: 'What AI skills should I learn for career growth?',        category: 'Skills'    },
  { text: 'How has global average salary changed since 2018?',       category: 'Salary'    },
  { text: 'Which roles have the highest automation risk?',           category: 'AI Impact' },
]

// ─────────────────────────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────────────────────────

interface Props {
  onNewChat:        () => void
  onLoadPrompt:     (text: string) => void
  sessions:         SessionSummary[]
  savedPrompts:     SavedPrompt[]
  onDeleteSession:  (id: string) => void
  onClearHistory:   () => void
  onDeletePrompt:   (id: string) => void
  sessionId:        string | null
  turnCount:        number
  mode:             ChatMode
  onModeChange:     (m: ChatMode) => void
  // Model config state (local to this sidebar)
}

// ─────────────────────────────────────────────────────────────────
// Sub-panels
// ─────────────────────────────────────────────────────────────────

function ChatPanel({
  sessionId, turnCount, onNewChat, mode, onModeChange,
}: Pick<Props, 'sessionId' | 'turnCount' | 'onNewChat' | 'mode' | 'onModeChange'>) {
  return (
    <div className="flex flex-col gap-3 p-3">
      {/* New chat button */}
      <button
        onClick={onNewChat}
        className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl
                   text-[12px] font-medium transition-all duration-150"
        style={{
          background: 'rgba(34,211,238,0.08)',
          border:     '1px solid rgba(34,211,238,0.25)',
          color:      '#22D3EE',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(34,211,238,0.15)' }}
        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(34,211,238,0.08)' }}
      >
        <Plus size={14} />
        New Conversation
      </button>

      {/* Session status */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Active Session
        </p>
        {sessionId ? (
          <>
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-1.5 h-1.5 rounded-full animate-pulse-dot" style={{ background: '#4ADE80' }} />
              <span className="font-mono text-[10px]" style={{ color: '#4ADE80' }}>Connected</span>
            </div>
            <p className="font-mono text-[10px] mb-1" style={{ color: '#8B949E' }}>
              ID: {sessionId.slice(0, 12)}…
            </p>
            <p className="font-mono text-[10px]" style={{ color: '#8B949E' }}>
              {turnCount} turn{turnCount !== 1 ? 's' : ''} · Memory active
            </p>
          </>
        ) : (
          <p className="font-mono text-[10px]" style={{ color: '#484F58' }}>
            No active session — ask a question to begin
          </p>
        )}
      </div>

      {/* Mode toggle */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Response Mode
        </p>
        <div className="flex gap-1.5">
          <button
            onClick={() => onModeChange('standard')}
            className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-[11px]
                       font-medium transition-all duration-150"
            style={mode === 'standard'
              ? { background: 'rgba(34,211,238,0.12)', border: '1px solid rgba(34,211,238,0.3)', color: '#22D3EE' }
              : { background: '#161B22',               border: '1px solid #21262D',              color: '#484F58'  }}
          >
            <Zap size={11} />
            Standard
          </button>
          <button
            onClick={() => onModeChange('multi-agent')}
            className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-[11px]
                       font-medium transition-all duration-150"
            style={mode === 'multi-agent'
              ? { background: 'rgba(129,140,248,0.12)', border: '1px solid rgba(129,140,248,0.3)', color: '#818CF8' }
              : { background: '#161B22',                border: '1px solid #21262D',               color: '#484F58'  }}
          >
            <Cpu size={11} />
            Multi-Agent
          </button>
        </div>
        <p className="font-mono text-[9px] mt-2 leading-relaxed" style={{ color: '#484F58' }}>
          {mode === 'multi-agent'
            ? 'Activates all 5 specialist agents for deep analysis.'
            : 'Fast single-model response with KPI + RAG context.'}
        </p>
      </div>

      {/* Capability list */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          AI Capabilities
        </p>
        {[
          { icon: Globe,       label: 'Global job market data'          },
          { icon: TrendingUp,  label: 'Salary benchmarks & trends'      },
          { icon: Brain,       label: 'Skill demand intelligence'        },
          { icon: ShieldCheck, label: 'AI disruption risk analysis'      },
          { icon: BookOpen,    label: 'Knowledge base (RAG)'             },
        ].map(({ icon: Icon, label }) => (
          <div key={label} className="flex items-center gap-2 mb-1.5 last:mb-0">
            <Icon size={11} style={{ color: '#22D3EE', flexShrink: 0 }} />
            <span className="text-[11px]" style={{ color: '#8B949E' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function HistoryPanel({
  sessions, onLoadPrompt, onDeleteSession, onClearHistory,
}: Pick<Props, 'sessions' | 'onLoadPrompt' | 'onDeleteSession' | 'onClearHistory'>) {
  if (!sessions.length) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 gap-3 p-6 text-center">
        <History size={28} style={{ color: '#21262D' }} />
        <p className="text-[12px]" style={{ color: '#484F58' }}>
          No conversations yet. Start chatting and your sessions will appear here.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 pt-3 pb-2">
        <p className="font-mono text-[9px] uppercase tracking-wider" style={{ color: '#484F58' }}>
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </p>
        <button
          onClick={onClearHistory}
          className="font-mono text-[9px] transition-colors"
          style={{ color: '#484F58' }}
          onMouseEnter={e => { e.currentTarget.style.color = '#F87171' }}
          onMouseLeave={e => { e.currentTarget.style.color = '#484F58' }}
        >
          Clear all
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1.5">
        {sessions.map(s => (
          <div
            key={s.id}
            className="group rounded-xl p-3 cursor-pointer transition-all duration-150"
            style={{ background: '#1C2333', border: '1px solid #21262D' }}
            onClick={() => onLoadPrompt(s.title)}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(34,211,238,0.2)' }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = '#21262D' }}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              {/* Intent dot */}
              <div className="flex items-center gap-1.5 min-w-0 flex-1">
                <div
                  className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                  style={{ background: INTENT_COLORS[s.intent] ?? '#8B949E' }}
                />
                <p className="text-[12px] font-medium truncate" style={{ color: '#E6EDF3' }}>
                  {s.title}
                </p>
              </div>
              {/* Delete button */}
              <button
                onClick={e => { e.stopPropagation(); onDeleteSession(s.id) }}
                className="opacity-0 group-hover:opacity-100 flex-shrink-0 transition-opacity p-0.5 rounded"
                style={{ color: '#484F58' }}
                onMouseEnter={e => { e.currentTarget.style.color = '#F87171' }}
                onMouseLeave={e => { e.currentTarget.style.color = '#484F58' }}
              >
                <X size={11} />
              </button>
            </div>

            {/* Preview */}
            {s.preview && (
              <p className="text-[10px] leading-relaxed mb-1.5 line-clamp-2"
                style={{ color: '#8B949E' }}>
                {s.preview}
              </p>
            )}

            {/* Meta */}
            <div className="flex items-center gap-2">
              <Clock size={9} style={{ color: '#484F58' }} />
              <span className="font-mono text-[9px]" style={{ color: '#484F58' }}>
                {relativeTime(s.lastActive)}
              </span>
              <span className="font-mono text-[9px]" style={{ color: '#484F58' }}>
                · {s.turnCount} turn{s.turnCount !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SavedPanel({
  savedPrompts, onLoadPrompt, onDeletePrompt,
}: Pick<Props, 'savedPrompts' | 'onLoadPrompt' | 'onDeletePrompt'>) {
  return (
    <div className="flex flex-col h-full">
      {/* Preset library */}
      <div className="px-3 pt-3 pb-2">
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Quick Prompts
        </p>
        <div className="space-y-1">
          {PRESET_PROMPTS.map((p, i) => (
            <button
              key={i}
              onClick={() => onLoadPrompt(p.text)}
              className="w-full text-left px-3 py-2 rounded-lg text-[11px] transition-all duration-150"
              style={{ border: '1px solid #21262D', color: '#8B949E' }}
              onMouseEnter={e => {
                e.currentTarget.style.background    = '#1C2333'
                e.currentTarget.style.borderColor   = 'rgba(34,211,238,0.2)'
                e.currentTarget.style.color         = '#E6EDF3'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background    = ''
                e.currentTarget.style.borderColor   = '#21262D'
                e.currentTarget.style.color         = '#8B949E'
              }}
            >
              <span className="font-mono text-[9px] block mb-0.5" style={{ color: '#484F58' }}>
                {p.category}
              </span>
              {p.text}
            </button>
          ))}
        </div>
      </div>

      {/* User-saved prompts */}
      {savedPrompts.length > 0 && (
        <div className="px-3 pb-3 flex-1 overflow-y-auto">
          <p className="font-mono text-[9px] uppercase tracking-wider mb-2 mt-2"
            style={{ color: '#484F58' }}>
            My Saved ({savedPrompts.length})
          </p>
          <div className="space-y-1">
            {savedPrompts.map(p => (
              <div
                key={p.id}
                className="group flex items-start gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all duration-150"
                style={{ border: '1px solid #21262D' }}
                onClick={() => onLoadPrompt(p.text)}
                onMouseEnter={e => {
                  const el = e.currentTarget as HTMLElement
                  el.style.background  = '#1C2333'
                  el.style.borderColor = 'rgba(34,211,238,0.2)'
                }}
                onMouseLeave={e => {
                  const el = e.currentTarget as HTMLElement
                  el.style.background  = ''
                  el.style.borderColor = '#21262D'
                }}
              >
                <p className="flex-1 text-[11px] leading-snug" style={{ color: '#8B949E' }}>
                  {p.text}
                </p>
                <button
                  onClick={e => { e.stopPropagation(); onDeletePrompt(p.id) }}
                  className="opacity-0 group-hover:opacity-100 flex-shrink-0 transition-opacity"
                  style={{ color: '#484F58' }}
                  onMouseEnter={e => { e.currentTarget.style.color = '#F87171' }}
                  onMouseLeave={e => { e.currentTarget.style.color = '#484F58' }}
                >
                  <X size={11} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function SettingsPanel({ mode, onModeChange }: Pick<Props, 'mode' | 'onModeChange'>) {
  return (
    <div className="flex flex-col gap-3 p-3">
      {/* Model info */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Model Settings
        </p>
        <div className="space-y-2">
          {[
            { label: 'Provider',    value: 'Groq'              },
            { label: 'Model',       value: 'llama-3.1-8b-instant' },
            { label: 'Max tokens',  value: '1,000'             },
            { label: 'Temperature', value: '0.3'               },
            { label: 'Timeout',     value: '60 seconds'        },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between">
              <span className="font-mono text-[10px]" style={{ color: '#484F58' }}>{label}</span>
              <span className="font-mono text-[10px]" style={{ color: '#8B949E' }}>{value}</span>
            </div>
          ))}
        </div>
        <p className="font-mono text-[9px] mt-2" style={{ color: '#484F58' }}>
          Configure in backend/.env → GROQ_MODEL
        </p>
      </div>

      {/* Data context */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Data Context
        </p>
        <p className="text-[11px] mb-2" style={{ color: '#8B949E' }}>
          The AI has access to these real platform datasets:
        </p>
        {[
          { label: 'Workforce analytics',    route: '/api/v1/workforce/*',   active: true  },
          { label: 'Salary intelligence',    route: '/api/v1/salary/*',      active: true  },
          { label: 'Skill intelligence',     route: '/api/v1/skills/*',      active: true  },
          { label: 'AI impact analysis',     route: '/api/v1/ai-impact/*',   active: true  },
          { label: 'RAG knowledge base',     route: 'ChromaDB / local docs', active: true  },
          { label: 'Forecast engine',        route: '/api/v1/forecast/*',    active: false },
        ].map(({ label, route, active }) => (
          <div key={label} className="flex items-center justify-between mb-1.5 last:mb-0">
            <div className="flex items-center gap-2">
              <div
                className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                style={{ background: active ? '#4ADE80' : '#21262D' }}
              />
              <span className="text-[11px]" style={{ color: active ? '#8B949E' : '#484F58' }}>
                {label}
              </span>
            </div>
            <span className="font-mono text-[9px]" style={{ color: '#484F58' }}>
              {active ? 'active' : 'phase 5'}
            </span>
          </div>
        ))}
      </div>

      {/* Memory info */}
      <div className="rounded-xl p-3" style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <p className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: '#484F58' }}>
          Memory System
        </p>
        {[
          { label: 'Backend',      value: 'Redis'         },
          { label: 'Max turns',    value: '10 per session'},
          { label: 'TTL',          value: '1 hour'        },
          { label: 'Local history', value: 'localStorage' },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between mb-1 last:mb-0">
            <span className="font-mono text-[10px]" style={{ color: '#484F58' }}>{label}</span>
            <span className="font-mono text-[10px]" style={{ color: '#8B949E' }}>{value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────
// Main ChatSidebar
// ─────────────────────────────────────────────────────────────────

export default function ChatSidebar(props: Props) {
  // ── Sync active tab with URL path ──────────────────────────────────
  // When the left app Sidebar navigates to /chat/history, /chat/saved,
  // /chat/settings, or /chat/context, open the matching tab automatically.
  // This makes the left nav items actually work as expected.
  const location = useLocation()

  function pathToTab(pathname: string): SidebarTab {
    if (pathname.startsWith('/chat/history'))  return 'history'
    if (pathname.startsWith('/chat/saved'))    return 'saved'
    if (pathname.startsWith('/chat/settings')) return 'settings'
    if (pathname.startsWith('/chat/context'))  return 'settings'  // context lives inside settings tab
    return 'chat'
  }

  const [activeTab, setActiveTab] = useState<SidebarTab>(() => pathToTab(location.pathname))

  // Keep tab in sync when user navigates via the left sidebar nav
  useEffect(() => {
    setActiveTab(pathToTab(location.pathname))
  }, [location.pathname])

  return (
    <aside
      className="flex flex-col w-[200px] flex-shrink-0 h-full border-r overflow-hidden"
      style={{ background: '#161B22', borderColor: '#21262D' }}
    >
      {/* Tab icon bar */}
      <div
        className="flex items-center justify-around px-1 py-2 border-b flex-shrink-0"
        style={{ borderColor: '#21262D' }}
      >
        {TABS.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            title={label}
            className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-lg
                       transition-all duration-150 group"
            style={{
              background: activeTab === id ? 'rgba(34,211,238,0.08)' : 'transparent',
              border:     activeTab === id ? '1px solid rgba(34,211,238,0.2)' : '1px solid transparent',
            }}
          >
            <Icon
              size={14}
              style={{ color: activeTab === id ? '#22D3EE' : '#484F58' }}
            />
            <span
              className="font-mono text-[8px] uppercase tracking-wider"
              style={{ color: activeTab === id ? '#22D3EE' : '#484F58' }}
            >
              {label}
            </span>
          </button>
        ))}
      </div>

      {/* Panel content — scrollable */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'chat'     && <ChatPanel     {...props} />}
        {activeTab === 'history'  && <HistoryPanel  {...props} />}
        {activeTab === 'saved'    && <SavedPanel    {...props} />}
        {activeTab === 'settings' && <SettingsPanel {...props} />}
      </div>
    </aside>
  )
}