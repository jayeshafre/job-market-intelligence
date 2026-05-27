import { useState, useCallback, useEffect } from 'react'
import type { ChatMessage } from '@/types/ai'

// ─────────────────────────────────────────
// useChatHistory
//
// Manages local session history using localStorage.
// No backend needed — fully client-side persistence.
//
// Each completed session is stored as a lightweight
// summary (not full messages, which could be large):
//   { id, title, intent, turnCount, startedAt, preview }
//
// The full messages[] for the ACTIVE session are
// managed by useChat — this hook only stores
// completed session summaries for the history panel.
//
// Storage key: "jmiq_chat_history"
// Max sessions kept: 20 (oldest pruned automatically)
// ─────────────────────────────────────────

const STORAGE_KEY  = 'jmiq_chat_history'
const MAX_SESSIONS = 20

export interface SessionSummary {
  id:         string     // session_id from backend (or local uuid)
  title:      string     // first user question, truncated to 60 chars
  preview:    string     // first AI answer, truncated to 100 chars
  intent:     string     // detected_intent of first response
  turnCount:  number
  startedAt:  string     // ISO string
  lastActive: string     // ISO string
}

export interface SavedPrompt {
  id:       string
  text:     string
  category: string
  savedAt:  string
}

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

function saveToStorage(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* ignore */ }
}

export function useChatHistory() {
  const [sessions, setSessions] = useState<SessionSummary[]>(() =>
    loadFromStorage<SessionSummary[]>(STORAGE_KEY, [])
  )

  const [savedPrompts, setSavedPrompts] = useState<SavedPrompt[]>(() =>
    loadFromStorage<SavedPrompt[]>('jmiq_saved_prompts', [])
  )

  // Persist sessions to localStorage whenever they change
  useEffect(() => {
    saveToStorage(STORAGE_KEY, sessions)
  }, [sessions])

  useEffect(() => {
    saveToStorage('jmiq_saved_prompts', savedPrompts)
  }, [savedPrompts])

  // ── Called by ChatAssistant when a conversation ends / is cleared ──
  const saveSession = useCallback((
    sessionId:  string,
    messages:   ChatMessage[],
    turnCount:  number,
  ) => {
    const userMsgs = messages.filter(m => m.role === 'user')
    const aiMsgs   = messages.filter(m => m.role === 'assistant' && !m.error)
    if (!userMsgs.length) return   // nothing to save

    const firstQ    = userMsgs[0].content
    const firstA    = aiMsgs[0]?.content ?? ''
    const firstIntent = aiMsgs[0]?.intent ?? 'general'

    const summary: SessionSummary = {
      id:         sessionId,
      title:      firstQ.length > 60 ? firstQ.slice(0, 57) + '…' : firstQ,
      preview:    firstA.replace(/[#*`\n]/g, ' ').slice(0, 100).trimEnd() + (firstA.length > 100 ? '…' : ''),
      intent:     firstIntent,
      turnCount,
      startedAt:  messages[0].timestamp.toISOString(),
      lastActive: messages[messages.length - 1].timestamp.toISOString(),
    }

    setSessions(prev => {
      // Remove duplicate if same session_id already stored, prepend new
      const filtered = prev.filter(s => s.id !== sessionId)
      return [summary, ...filtered].slice(0, MAX_SESSIONS)
    })
  }, [])

  const deleteSession = useCallback((id: string) => {
    setSessions(prev => prev.filter(s => s.id !== id))
  }, [])

  const clearAllHistory = useCallback(() => {
    setSessions([])
  }, [])

  // ── Saved prompts ──────────────────────────────────────────────────

  const savePrompt = useCallback((text: string, category: string) => {
    const prompt: SavedPrompt = {
      id:       crypto.randomUUID(),
      text,
      category,
      savedAt:  new Date().toISOString(),
    }
    setSavedPrompts(prev => [prompt, ...prev].slice(0, 50))
  }, [])

  const deletePrompt = useCallback((id: string) => {
    setSavedPrompts(prev => prev.filter(p => p.id !== id))
  }, [])

  return {
    sessions,
    savedPrompts,
    saveSession,
    deleteSession,
    clearAllHistory,
    savePrompt,
    deletePrompt,
  }
}