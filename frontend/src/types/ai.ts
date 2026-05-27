// ─────────────────────────────────────────
// types/ai.ts
//
// Mirrors backend/api/schemas/ai.py exactly.
// Every field name matches the Pydantic model.
//
// We use the most capable endpoint (v6) as
// the primary chat interface — it gives:
//   - intent detection        (orchestrator.py)
//   - KPI context injection   (kpi_context.py)
//   - RAG document retrieval  (rag_pipeline.py)
//   - recommendations         (recommendation_engine.py)
//   - conversation memory     (memory.py / Redis)
//
// v7 (multi-agent) is used for "deep analysis"
// mode — shows agent execution panel in UI.
// ─────────────────────────────────────────

// ── Request shapes ────────────────────────

// Used by v1–v5 (ChatRequest)
export interface ChatRequest {
  question: string    // min 5, max 500 chars
  context?: string    // default: "global job market and workforce analytics"
}

// Used by v6–v7 (MemoryChatRequest)
export interface MemoryChatRequest {
  question:   string
  context?:   string
  session_id: string | null   // null = start new session, reuse to continue
}

// ── Intent type ───────────────────────────
// Maps to orchestrator.py Intent enum values

export type ChatIntent =
  | 'salary'
  | 'skills'
  | 'hiring'
  | 'ai_disruption'
  | 'forecast'
  | 'general'

// ── Recommendation (from v4+) ─────────────
// Matches backend Recommendation schema

export interface Recommendation {
  title:            string   // Short action-oriented title
  category:         string   // role | skill | country | industry | career_pivot
  rationale:        string   // Why this is recommended
  priority:         string   // high | medium | low
  estimated_impact: string   // e.g. "+23% salary"
}

// ── RAG retrieved chunk (from v5+) ────────
// Matches backend RetrievedChunk schema

export interface RetrievedChunk {
  text:       string   // The retrieved document text
  doc_id:     string   // Source document identifier
  similarity: number   // Cosine similarity 0–1
}

// ── Agent output (from v7) ────────────────
// Matches backend AgentOutput schema

export interface AgentOutput {
  agent_name: string      // e.g. "SalaryAgent"
  domain:     string      // salary | skills | hiring | ai_disruption | forecast
  success:    boolean
  insights:   string[]    // Key insight strings from the agent
  error:      string      // Error message if success=false
}

// ── Response shapes ───────────────────────

// v1 — basic
export interface ChatResponse {
  answer:      string
  model:       string
  tokens_used: number
  question:    string
}

// v2 — + intent
export interface OrchestratedChatResponse extends ChatResponse {
  detected_intent: ChatIntent
}

// v3 — + KPI context flag
export interface KPIEnrichedChatResponse extends OrchestratedChatResponse {
  kpi_context_used: boolean
}

// v4 — + recommendations
export interface RecommendationResponse extends KPIEnrichedChatResponse {
  recommendations:       Recommendation[]
  recommendations_parsed: boolean
}

// v5 — + RAG
export interface RAGChatResponse extends RecommendationResponse {
  rag_used:          boolean
  chunks_retrieved:  number
  retrieved_chunks:  RetrievedChunk[]
}

// v6 — + memory (PRIMARY ENDPOINT)
export interface MemoryChatResponse extends RAGChatResponse {
  session_id:     string    // Store this, send in next request
  turn_count:     number    // How many turns in this session
  memory_used:    boolean   // True if history was injected
  is_new_session: boolean   // True on first message
}

// v7 — multi-agent synthesis
export interface MultiAgentResponse {
  question:       string
  synthesis:      string          // Final unified answer (not "answer")
  agent_outputs:  AgentOutput[]
  execution_plan: string[]
  agents_run:     number
  agents_failed:  number
  tokens_used:    number
  model:          string
}

// ── UI-level message type ─────────────────
// What the frontend stores per chat turn.
// Combines both user input and AI response.

export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id:           string           // uuid for React key
  role:         MessageRole
  content:      string           // The text to display
  timestamp:    Date
  // Assistant-only enrichment fields (from MemoryChatResponse)
  intent?:      ChatIntent
  kpi_backed?:  boolean          // kpi_context_used
  rag_used?:    boolean
  chunks?:      RetrievedChunk[]
  recommendations?: Recommendation[]
  // Multi-agent mode
  is_multi_agent?: boolean
  agent_outputs?:  AgentOutput[]
  execution_plan?: string[]
  agents_run?:     number
  // Meta
  tokens_used?: number
  model?:       string
  error?:       string           // If API call failed
}

// ── Session state ─────────────────────────

export interface ChatSession {
  session_id:  string
  turn_count:  number
  started_at:  Date
  last_active: Date
  messages:    ChatMessage[]
}

// ── Chat mode ─────────────────────────────

export type ChatMode = 'standard' | 'multi-agent'