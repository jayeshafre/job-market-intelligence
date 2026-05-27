import { aiApi } from './api'
import type {
  MemoryChatRequest,
  MemoryChatResponse,
  MultiAgentResponse,
} from '@/types/ai'

// ─────────────────────────────────────────
// aiChatService.ts
//
// Uses aiApi (60s timeout) instead of the
// default api (15s) because Groq LLM calls
// + RAG embedding + Redis memory can easily
// take 20–40s on first cold request.
//
// Endpoint chain (fallback on error):
//
//   PRIMARY:  POST /api/v1/ai/chat/v6
//     Full stack: memory + RAG + KPI + recommendations
//     Request:  { question, context, session_id }
//     Response: MemoryChatResponse
//
//   FALLBACK: POST /api/v1/ai/chat/v3
//     Lighter: intent + KPI context, no Redis/RAG
//     Use this if Redis is not running.
//     Response: KPIEnrichedChatResponse (subset of MemoryChatResponse)
//
// The fallback makes the chatbot work even if Redis
// or ChromaDB isn't set up yet, with a degraded-mode
// warning shown in the UI.
// ─────────────────────────────────────────

// ── Primary: v6 (memory + RAG + KPI + recommendations) ──

export async function sendChatMessage(
  question:  string,
  sessionId: string | null,
  context =  'global job market and workforce analytics',
): Promise<MemoryChatResponse & { _degraded?: boolean; _degraded_reason?: string }> {

  const body: MemoryChatRequest = { question, context, session_id: sessionId }

  try {
    // Attempt full v6 (memory + RAG + KPI + recommendations)
    const res = await aiApi.post<MemoryChatResponse>('/ai/chat/v6', body)
    return res.data

  } catch (v6Error) {
    const errMsg = v6Error instanceof Error ? v6Error.message : String(v6Error)

    // If v6 fails due to Redis/RAG, try v3 (no memory, no RAG)
    const isInfraError =
      errMsg.toLowerCase().includes('redis') ||
      errMsg.toLowerCase().includes('chroma') ||
      errMsg.toLowerCase().includes('embedding') ||
      errMsg.toLowerCase().includes('500')

    if (isInfraError) {
      console.warn('[aiChatService] v6 failed, falling back to v3:', errMsg)
      try {
        // v3: intent detection + KPI context, no Redis/RAG required
        const fallbackRes = await aiApi.post<any>('/ai/chat/v3', {
          question,
          context,
        })
        // Shape the v3 response to match MemoryChatResponse interface
        return {
          ...fallbackRes.data,
          // Provide defaults for fields v3 doesn't return
          session_id:            null as any,
          turn_count:            0,
          memory_used:           false,
          is_new_session:        true,
          rag_used:              false,
          chunks_retrieved:      0,
          retrieved_chunks:      [],
          recommendations:       [],
          recommendations_parsed: false,
          // Mark as degraded so UI can show a warning
          _degraded:             true,
          _degraded_reason:      errMsg,
        }
      } catch (v3Error) {
        // Both endpoints failed — rethrow the original v6 error
        throw v6Error
      }
    }

    // Non-infra error (timeout, network, Groq auth) — rethrow as-is
    throw v6Error
  }
}

// ── Multi-agent: v7 ──

export async function sendMultiAgentMessage(
  question:  string,
  sessionId: string | null,
  context =  'global job market and workforce analytics',
): Promise<MultiAgentResponse> {
  const body: MemoryChatRequest = { question, context, session_id: sessionId }
  const res = await aiApi.post<MultiAgentResponse>('/ai/chat/v7', body)
  return res.data
}

// ── Clear Redis session ──

export async function clearChatSession(sessionId: string): Promise<void> {
  try {
    await aiApi.delete(`/ai/session/${sessionId}`)
  } catch {
    // Silently ignore — session will expire via Redis TTL anyway
  }
}