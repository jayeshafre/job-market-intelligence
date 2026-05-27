import axios from 'axios'

// ─────────────────────────────────────────
// api.ts — Central Axios instance
//
// Two instances:
//   api        — analytics endpoints, 15s timeout
//   aiApi      — AI/chat endpoints, 60s timeout
//
// Why separate timeouts?
//   Analytics endpoints: simple DB queries, <2s
//   AI chat endpoints:   Groq LLM call + RAG embedding
//                        + Redis memory + KPI injection
//                        can take 20–40s on cold start.
//   A 15s timeout kills AI requests before Groq responds.
// ─────────────────────────────────────────

function createInstance(timeout: number) {
  const instance = axios.create({
    baseURL: '/api/v1',
    timeout,
    headers: { 'Content-Type': 'application/json' },
  })

  instance.interceptors.request.use(
    config => config,
    error => Promise.reject(error)
  )

  instance.interceptors.response.use(
    response => response,
    error => {
      // Build a useful diagnostic message
      let message = 'An unexpected error occurred'

      if (error.code === 'ECONNABORTED') {
        message = `Request timed out after ${Math.round(timeout / 1000)}s. ` +
          'Check that FastAPI is running and not hanging on Redis/Groq.'
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        message = 'Cannot reach backend. Is FastAPI running on localhost:8000?'
      } else if (error.response?.status === 500) {
        // FastAPI 500 — try to extract the detail message
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          if (detail.includes('Redis') || detail.includes('redis')) {
            message = 'Redis not running. Start Redis: redis-server'
          } else if (detail.includes('GROQ') || detail.includes('groq')) {
            message = 'Groq API error. Check GROQ_API_KEY in your .env file.'
          } else if (detail.includes('chroma') || detail.includes('embedding')) {
            message = 'RAG pipeline error. Run: pip install chromadb sentence-transformers'
          } else {
            message = `Backend error: ${detail}`
          }
        } else {
          message = 'Internal server error (500). Check FastAPI terminal for traceback.'
        }
      } else if (error.response?.status === 422) {
        message = 'Invalid request — check question length (min 5 chars, max 500).'
      } else if (error.response?.status === 404) {
        message = `Endpoint not found: ${error.config?.url}. Check main.py router registration.`
      } else {
        message =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          message
      }

      console.error('[API Error]', error.config?.url, message)
      return Promise.reject(new Error(message))
    }
  )

  return instance
}

// ── Standard analytics instance (15s) ────
const api = createInstance(15_000)

// ── AI chat instance (60s) ────────────────
// Groq LLM + RAG + Redis can easily take 30s+
export const aiApi = createInstance(60_000)

export default api