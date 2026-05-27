import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppModeProvider } from '@/context/AppModeContext'
import AppShell from '@/components/layout/AppShell'
import PlaceholderPage from '@/components/shared/PlaceholderPage'

// ─────────────────────────────────────────
// Page imports — all dashboard pages wired
//
// Phase 1 ✓  Layout shell, Sidebar, Topbar
// Phase 2 ✓  MainDashboard, LiveAnalytics
// Phase 3 ✓  WorkforceAnalytics, SalaryIntelligence,
//             SkillIntelligence, AiImpactAnalysis
// Phase 3b ✓ Forecasting, Recommendations,
//             DataExplorer, Reports
// Phase 4    Chatbot pages (pending AI router files)
// ─────────────────────────────────────────

// Phase 2
import MainDashboard      from '@/pages/dashboard/MainDashboard'
import LiveAnalytics      from '@/pages/dashboard/LiveAnalytics'

// Phase 3
import WorkforceAnalytics from '@/pages/dashboard/WorkforceAnalytics'
import SalaryIntelligence from '@/pages/dashboard/SalaryIntelligence'
import SkillIntelligence  from '@/pages/dashboard/SkillIntelligence'
import AiImpactAnalysis   from '@/pages/dashboard/AiImpactAnalysis'

// Phase 3b — remaining dashboard pages
import Forecasting        from '@/pages/dashboard/Forecasting'
import Recommendations    from '@/pages/dashboard/Recommendations'
import DataExplorer       from '@/pages/dashboard/DataExplorer'
import Reports            from '@/pages/dashboard/Reports'

// Chatbot pages
import ChatAssistant from '@/pages/chat/ChatAssistant'

export default function App() {
  return (
    <BrowserRouter>
      <AppModeProvider>
        <Routes>
          {/* Root → Main Dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* All pages share the AppShell layout (Sidebar + Topbar) */}
          <Route element={<AppShell />}>

            {/* ── Dashboard routes ── */}

            {/* Overview */}
            <Route path="/dashboard"       element={<MainDashboard />} />
            <Route path="/dashboard/live"  element={<LiveAnalytics />} />

            {/* Intelligence */}
            <Route path="/dashboard/workforce"  element={<WorkforceAnalytics />} />
            <Route path="/dashboard/salary"     element={<SalaryIntelligence />} />
            <Route path="/dashboard/skills"     element={<SkillIntelligence />}  />
            <Route path="/dashboard/ai-impact"  element={<AiImpactAnalysis />}   />

            {/* Predictive */}
            <Route path="/dashboard/forecasting"     element={<Forecasting />}     />
            <Route path="/dashboard/recommendations" element={<Recommendations />} />

            {/* Data */}
            <Route path="/dashboard/data-explorer" element={<DataExplorer />} />
            <Route path="/dashboard/reports"       element={<Reports />}      />

              {/* ── Chatbot routes ── */}
            <Route path="/chat"          element={<ChatAssistant />} />
            <Route path="/chat/history"  element={<ChatAssistant />} />
            <Route path="/chat/saved"    element={<ChatAssistant />} />
            <Route path="/chat/settings" element={<ChatAssistant />} />
            <Route path="/chat/context"  element={<ChatAssistant />} />
 

          </Route>

          {/* Catch-all → back to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AppModeProvider>
    </BrowserRouter>
  )
}