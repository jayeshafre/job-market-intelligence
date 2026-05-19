import { Outlet } from 'react-router-dom'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'

// ─────────────────────────────────────────
// AppShell
//
// Root layout wrapper. Structure:
//
//  ┌──────────┬──────────────────────────┐
//  │          │  Topbar                  │
//  │ Sidebar  ├──────────────────────────┤
//  │          │                          │
//  │          │  <Outlet />              │
//  │          │  (current page content)  │
//  │          │                          │
//  └──────────┴──────────────────────────┘
//
// <Outlet /> is filled in by React Router
// based on the active route.
// ─────────────────────────────────────────

export default function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden bg-base-900">
      {/* Fixed-width sidebar */}
      <Sidebar />

      {/* Right column: topbar + scrollable content */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Topbar />

        {/* Main content area — each page renders here */}
        <main
          className="flex-1 overflow-y-auto bg-base-900 p-6"
          id="main-content"
        >
          {/* React Router injects the active page component here */}
          <Outlet />
        </main>
      </div>
    </div>
  )
}