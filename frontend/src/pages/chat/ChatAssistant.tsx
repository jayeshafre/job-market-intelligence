import { useEffect, useRef, useState } from 'react'
import { Globe, Trash2, PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { useChat } from '@/hooks/useChat'
import { useChatHistory } from '@/hooks/useChatHistory'
import { useSuggestedPrompts } from '@/hooks/useSuggestedPrompts'
import ChatMessage from '@/components/chat/ChatMessage'
import ChatInput from '@/components/chat/ChatInput'
import TypingIndicator from '@/components/chat/TypingIndicator'
import SuggestedPrompts from '@/components/chat/SuggestedPrompts'
import ChatSidebar from '@/components/chat/ChatSidebar'

// ─────────────────────────────────────────
// ChatAssistant — full chat page
//
// Layout:
//   ┌──────────────┬──────────────────────────────┐
//   │              │  Header                       │
//   │  ChatSidebar ├──────────────────────────────┤
//   │  (200px)     │  Scroll area                  │
//   │              │  (messages / welcome)         │
//   │  4 tabs:     ├──────────────────────────────┤
//   │  chat        │  ChatInput (pinned bottom)    │
//   │  history     └──────────────────────────────┘
//   │  saved
//   │  settings
//   └──────────────
//
// Sidebar can be collapsed with the toggle button.
//
// Data flow:
//   useChat         → sends messages, manages session_id
//   useChatHistory  → saves completed sessions to localStorage
//   ChatSidebar     → reads history, triggers onNewChat / onLoadPrompt
// ─────────────────────────────────────────

export default function ChatAssistant() {
  const {
    messages,
    sessionId,
    isLoading,
    mode,
    turnCount,
    setMode,
    sendMessage,
    clearSession,
  } = useChat()

  const {
    sessions,
    savedPrompts,
    saveSession,
    deleteSession,
    clearAllHistory,
    deletePrompt,
  } = useChatHistory()

  const messagesEndRef  = useRef<HTMLDivElement>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Save session to history whenever it ends (cleared) or has messages
  // We save on every new assistant message so history stays current
  useEffect(() => {
    const hasMessages = messages.some(m => m.role === 'assistant' && !m.error)
    if (hasMessages && sessionId) {
      saveSession(sessionId, messages, turnCount)
    }
  }, [messages, sessionId, turnCount, saveSession])

  // Suggested prompts — only shown on empty chat
  const isEmpty = messages.length === 0
  const { defaultPrompts } = useSuggestedPrompts(undefined)

  // ── New chat: save current session, then clear ──
  function handleNewChat() {
    if (messages.length > 0 && sessionId) {
      saveSession(sessionId, messages, turnCount)
    }
    clearSession()
  }

  // ── Load a prompt from history / saved panel ──
  // Puts text directly into the chat by sending it
  function handleLoadPrompt(text: string) {
    sendMessage(text)
  }

  return (
    <div className="flex h-full overflow-hidden" style={{ background: '#0D1117' }}>

      {/* ── ChatSidebar ── collapsible */}
      {sidebarOpen && (
        <ChatSidebar
          onNewChat={handleNewChat}
          onLoadPrompt={handleLoadPrompt}
          sessions={sessions}
          savedPrompts={savedPrompts}
          onDeleteSession={deleteSession}
          onClearHistory={clearAllHistory}
          onDeletePrompt={deletePrompt}
          sessionId={sessionId}
          turnCount={turnCount}
          mode={mode}
          onModeChange={setMode}
        />
      )}

      {/* ── Main chat area ── */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">

        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 border-b flex-shrink-0"
          style={{ background: '#161B22', borderColor: '#21262D' }}
        >
          <div className="flex items-center gap-3">
            {/* Sidebar toggle */}
            <button
              onClick={() => setSidebarOpen(v => !v)}
              title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
              className="p-1.5 rounded-lg transition-colors duration-150"
              style={{ color: '#484F58' }}
              onMouseEnter={e => { e.currentTarget.style.color = '#8B949E' }}
              onMouseLeave={e => { e.currentTarget.style.color = '#484F58' }}
            >
              {sidebarOpen
                ? <PanelLeftClose size={15} />
                : <PanelLeftOpen  size={15} />}
            </button>

            {/* Brand */}
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.2)' }}
            >
              <Globe size={15} style={{ color: '#22D3EE' }} />
            </div>

            <div>
              <p className="text-[13px] font-semibold" style={{ color: '#E6EDF3' }}>
                AI Workforce Assistant
              </p>
              <div className="flex items-center gap-2">
                <div
                  className="w-1.5 h-1.5 rounded-full animate-pulse-dot"
                  style={{ background: '#4ADE80' }}
                />
                <p className="font-mono text-[10px]" style={{ color: '#484F58' }}>
                  {sessionId
                    ? `Session active · ${turnCount} turn${turnCount !== 1 ? 's' : ''} · memory on`
                    : 'Ready — ask anything about the job market'}
                </p>
              </div>
            </div>
          </div>

          {/* Right: session id + clear */}
          <div className="flex items-center gap-2">
            {sessionId && (
              <span
                className="font-mono text-[9px] hidden sm:block"
                style={{ color: '#484F58' }}
              >
                {sessionId.slice(0, 8)}…
              </span>
            )}
            <button
              onClick={handleNewChat}
              disabled={isLoading || isEmpty}
              title="Save and start new conversation"
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px]
                         border transition-all duration-150 disabled:opacity-40"
              style={{ color: '#8B949E', borderColor: '#21262D' }}
              onMouseEnter={e => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.color       = '#F87171'
                  e.currentTarget.style.borderColor = 'rgba(248,113,113,0.3)'
                }
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color       = '#8B949E'
                e.currentTarget.style.borderColor = '#21262D'
              }}
            >
              <Trash2 size={12} />
              Clear
            </button>
          </div>
        </div>

        {/* ── Scrollable message area ── */}
        <div className="flex-1 overflow-y-auto px-4 pt-4 pb-2">

          {/* Welcome screen + prompts — only on empty chat */}
          {isEmpty && (
            <>
              <div className="flex flex-col items-center justify-center py-8 gap-4 mb-4">
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center"
                  style={{ background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.2)' }}
                >
                  <Globe size={24} style={{ color: '#22D3EE' }} />
                </div>

                <div className="text-center">
                  <h2 className="text-[16px] font-semibold mb-1.5" style={{ color: '#E6EDF3' }}>
                    Global Job Market Intelligence
                  </h2>
                  <p className="text-[12px] max-w-sm leading-relaxed" style={{ color: '#8B949E' }}>
                    Ask me about hiring trends, salary benchmarks, in-demand skills,
                    AI disruption risk, or workforce forecasts. Backed by real platform
                    data, knowledge base, and conversation memory.
                  </p>
                </div>

                {/* Capability chips */}
                <div className="flex flex-wrap justify-center gap-2">
                  {[
                    'Salary data', 'Skill trends', 'Hiring patterns',
                    'AI risk', 'Forecasts', 'Knowledge base', 'Memory',
                  ].map(cap => (
                    <span
                      key={cap}
                      className="font-mono text-[9px] px-2.5 py-1 rounded-full"
                      style={{
                        background: 'rgba(34,211,238,0.06)',
                        border:     '1px solid rgba(34,211,238,0.15)',
                        color:      '#8B949E',
                      }}
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>

              {/* Suggested prompts — only before first message */}
              <SuggestedPrompts
                prompts={defaultPrompts}
                onSelect={sendMessage}
                label="Try asking"
              />
            </>
          )}

          {/* Messages */}
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {/* Typing indicator */}
          {isLoading && <TypingIndicator />}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} className="h-2" />
        </div>

        {/* ── Input bar — always pinned to bottom ── */}
        <div
          className="flex-shrink-0 border-t"
          style={{ borderColor: '#21262D', background: '#0D1117' }}
        >
          <ChatInput
            onSend={sendMessage}
            isLoading={isLoading}
            mode={mode}
            onModeChange={setMode}
          />
        </div>
      </div>
    </div>
  )
}