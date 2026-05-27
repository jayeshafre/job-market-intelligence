import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'

// ─────────────────────────────────────────
// AppShell
//
// FIX: Chat pages need full-height, zero-padding
// layout so ChatAssistant can control its own
// internal scroll and keep the input pinned.
//
// Dashboard pages keep their p-6 padding and
// overflow-y-auto scroll behaviour.
//
// Detection: any route starting with /chat
// gets the chat layout (no padding, no scroll).
// All other routes get the dashboard layout.
// ─────────────────────────────────────────

export default function AppShell() {
  const location = useLocation()
  const isChatRoute = location.pathname.startsWith('/chat')

  return (
    <div className="flex h-screen overflow-hidden bg-base-900">
      {/* Fixed-width sidebar */}
      <Sidebar />

      {/* Right column: topbar + content */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Topbar />

        {isChatRoute ? (
          // ── Chat layout: full height, no padding, no outer scroll ──
          // ChatAssistant manages its own internal scroll and sticky input.
          <main
            className="flex-1 overflow-hidden"
            id="main-content"
            style={{ background: '#0D1117' }}
          >
            <Outlet />
          </main>
        ) : (
          // ── Dashboard layout: padded, scrollable ──
          <main
            className="flex-1 overflow-y-auto p-6"
            id="main-content"
            style={{ background: '#0D1117' }}
          >
            <Outlet />
          </main>
        )}
      </div>
    </div>
  )
}