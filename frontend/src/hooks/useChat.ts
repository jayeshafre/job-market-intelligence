import { useState, useCallback, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { sendChatMessage, sendMultiAgentMessage, clearChatSession } from '@/services/aiChatService'
import type { ChatMessage, ChatMode, MemoryChatResponse, MultiAgentResponse } from '@/types/ai'

// ─────────────────────────────────────────
// useChat
//
// Updated to handle _degraded flag from
// aiChatService fallback — shows a warning
// badge in the message when running without
// Redis/RAG (v3 degraded mode).
// ─────────────────────────────────────────

export type SendStatus = 'idle' | 'sending' | 'error'

interface UseChatReturn {
  messages:     ChatMessage[]
  sessionId:    string | null
  isLoading:    boolean
  status:       SendStatus
  error:        string | null
  mode:         ChatMode
  turnCount:    number
  setMode:      (m: ChatMode) => void
  sendMessage:  (question: string) => Promise<void>
  clearSession: () => Promise<void>
  clearMessages:() => void
}

export function useChat(): UseChatReturn {
  const [messages,  setMessages]  = useState<ChatMessage[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [status,    setStatus]    = useState<SendStatus>('idle')
  const [error,     setError]     = useState<string | null>(null)
  const [mode,      setMode]      = useState<ChatMode>('standard')
  const [turnCount, setTurnCount] = useState(0)

  const sessionRef = useRef<string | null>(null)

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages(prev => [...prev, msg])
  }, [])

  // Build assistant message from v6 (or degraded v3) response
  function buildAssistantMessage(
    res: MemoryChatResponse & { _degraded?: boolean; _degraded_reason?: string }
  ): ChatMessage {
    return {
      id:              uuidv4(),
      role:            'assistant',
      content:         res.answer,
      timestamp:       new Date(),
      intent:          res.detected_intent as any,
      kpi_backed:      res.kpi_context_used,
      rag_used:        res.rag_used,
      chunks:          res.retrieved_chunks ?? [],
      recommendations: res.recommendations ?? [],
      tokens_used:     res.tokens_used,
      model:           res.model,
      is_multi_agent:  false,
      // Pass degraded flag through so ChatMessage can show warning
      error:           res._degraded
        ? `Running in degraded mode (no memory/RAG): ${res._degraded_reason}`
        : undefined,
    }
  }

  function buildMultiAgentMessage(res: MultiAgentResponse): ChatMessage {
    return {
      id:             uuidv4(),
      role:           'assistant',
      content:        res.synthesis,
      timestamp:      new Date(),
      is_multi_agent: true,
      agent_outputs:  res.agent_outputs,
      execution_plan: res.execution_plan,
      agents_run:     res.agents_run,
      tokens_used:    res.tokens_used,
      model:          res.model,
    }
  }

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || isLoading) return

    setError(null)
    setStatus('sending')

    // Add user message immediately (optimistic)
    addMessage({
      id:        uuidv4(),
      role:      'user',
      content:   question.trim(),
      timestamp: new Date(),
    })
    setIsLoading(true)

    try {
      if (mode === 'standard') {
        const res = await sendChatMessage(question, sessionRef.current)

        // Store session_id on first successful v6 response
        if (res.session_id && !sessionRef.current) {
          sessionRef.current = res.session_id
          setSessionId(res.session_id)
        }
        if (res.turn_count) setTurnCount(res.turn_count)

        // Build message — if degraded, error field carries the warning
        const msg = buildAssistantMessage(res)

        // For degraded mode: show the answer but add a visible note
        if (res._degraded) {
          addMessage({
            ...msg,
            // Clear error so it doesn't show the red "backend unreachable" bubble
            // Instead show the answer normally — degraded is still a working response
            error: undefined,
            // Add a degraded note to the content
            content: res.answer + '\n\n---\n*⚠ Running without memory/RAG (Redis or ChromaDB not available). Answers are still Groq-powered with KPI context.*',
          })
        } else {
          addMessage(msg)
        }

      } else {
        const res = await sendMultiAgentMessage(question, sessionRef.current)
        addMessage(buildMultiAgentMessage(res))
      }

      setStatus('idle')

    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Failed to reach AI backend'
      setError(errMsg)
      setStatus('error')

      addMessage({
        id:        uuidv4(),
        role:      'assistant',
        content:   '',
        timestamp: new Date(),
        error:     errMsg,
      })
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, mode, addMessage])

  const clearSession = useCallback(async () => {
    if (sessionRef.current) {
      await clearChatSession(sessionRef.current)
      sessionRef.current = null
      setSessionId(null)
    }
    setMessages([])
    setTurnCount(0)
    setError(null)
    setStatus('idle')
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages, sessionId, isLoading, status, error,
    mode, turnCount, setMode, sendMessage, clearSession, clearMessages,
  }
}