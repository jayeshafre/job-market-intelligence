import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppModeProvider } from '@/context/AppModeContext'
import AppShell from '@/components/layout/AppShell'
import PlaceholderPage from '@/components/shared/PlaceholderPage'

// ─────────────────────────────────────────
// Page imports — add real pages here as
// each phase is completed.
//
// Phase 2 ✓  MainDashboard
// Phase 3    Workforce, Salary, Skills, AI Impact
// Phase 4    Chatbot pages
// Phase 5    Forecasting, Recommendations, Data Explorer
// ─────────────────────────────────────────
import MainDashboard from '@/pages/dashboard/MainDashboard'

export default function App() {
  return (
    <BrowserRouter>
      {/* AppModeProvider makes mode + toggleMode available everywhere */}
      <AppModeProvider>
        <Routes>
          {/* Root redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* ── App shell wraps all pages ── */}
          <Route element={<AppShell />}>

            {/* ── Dashboard routes ── */}
            {/* Phase 2 ✓ — real page */}
            <Route path="/dashboard" element={<MainDashboard />} />
            <Route
              path="/dashboard/live"
              element={
                <PlaceholderPage
                  title="Live Analytics"
                  phase="Phase 2"
                  description="Real-time metrics with WebSocket-powered auto-refresh."
                />
              }
            />
            <Route
              path="/dashboard/workforce"
              element={
                <PlaceholderPage
                  title="Workforce Analytics"
                  phase="Phase 3"
                  description="Hiring trends, country-wise demand, remote work breakdown."
                />
              }
            />
            <Route
              path="/dashboard/salary"
              element={
                <PlaceholderPage
                  title="Salary Intelligence"
                  phase="Phase 3"
                  description="Salary comparison by role, country-wise insights, trend charts."
                />
              }
            />
            <Route
              path="/dashboard/skills"
              element={
                <PlaceholderPage
                  title="Skill Intelligence"
                  phase="Phase 3"
                  description="Fastest growing skills, AI adoption trends, technology demand."
                />
              }
            />
            <Route
              path="/dashboard/ai-impact"
              element={
                <PlaceholderPage
                  title="AI Impact Analysis"
                  phase="Phase 3"
                  description="Automation risk scores, AI disruption analysis, future-safe careers."
                />
              }
            />
            <Route
              path="/dashboard/forecasting"
              element={
                <PlaceholderPage
                  title="Forecasting"
                  phase="Phase 5"
                  description="Prophet-powered hiring & salary forecasts, trend visualization."
                />
              }
            />
            <Route
              path="/dashboard/recommendations"
              element={
                <PlaceholderPage
                  title="Recommendations"
                  phase="Phase 5"
                  description="AI-generated insight cards, career suggestions, skill gaps."
                />
              }
            />
            <Route
              path="/dashboard/data-explorer"
              element={
                <PlaceholderPage
                  title="Data Explorer"
                  phase="Phase 5"
                  description="Searchable, filterable tables across all datasets."
                />
              }
            />
            <Route
              path="/dashboard/reports"
              element={
                <PlaceholderPage
                  title="Reports"
                  phase="Phase 5"
                  description="Exportable analytics reports and summaries."
                />
              }
            />

            {/* ── Chatbot routes (Phase 4) ── */}
            <Route
              path="/chat"
              element={
                <PlaceholderPage
                  title="AI Assistant"
                  phase="Phase 4"
                  description="Groq-powered chat with streaming responses and markdown support."
                />
              }
            />
            <Route
              path="/chat/history"
              element={
                <PlaceholderPage
                  title="Chat History"
                  phase="Phase 4"
                  description="Browse and resume past AI conversations."
                />
              }
            />
            <Route
              path="/chat/saved"
              element={
                <PlaceholderPage
                  title="Saved Prompts"
                  phase="Phase 4"
                  description="Quick-access library of useful analysis prompts."
                />
              }
            />
            <Route
              path="/chat/settings"
              element={
                <PlaceholderPage
                  title="Model Settings"
                  phase="Phase 4"
                  description="Configure AI model, temperature, and response style."
                />
              }
            />
            <Route
              path="/chat/context"
              element={
                <PlaceholderPage
                  title="Data Context"
                  phase="Phase 4"
                  description="Select which datasets the AI assistant can query."
                />
              }
            />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AppModeProvider>
    </BrowserRouter>
  )
}