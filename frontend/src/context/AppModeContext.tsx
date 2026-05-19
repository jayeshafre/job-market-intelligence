import React, { createContext, useContext, useState, useCallback } from 'react'
import type { AppMode } from '@/types/navigation'

// ─────────────────────────────────────────
// Context shape
// ─────────────────────────────────────────

interface AppModeContextValue {
  mode: AppMode
  isDashboard: boolean
  isChatbot: boolean
  toggleMode: () => void
  setMode: (mode: AppMode) => void
}

// ─────────────────────────────────────────
// Create context with a safe default
// ─────────────────────────────────────────

const AppModeContext = createContext<AppModeContextValue | null>(null)

// ─────────────────────────────────────────
// Provider component
// Wrap this around <App /> so every child
// can read / toggle the app mode.
// ─────────────────────────────────────────

export function AppModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<AppMode>('dashboard')

  const toggleMode = useCallback(() => {
    setModeState((prev) => (prev === 'dashboard' ? 'chatbot' : 'dashboard'))
  }, [])

  const setMode = useCallback((newMode: AppMode) => {
    setModeState(newMode)
  }, [])

  const value: AppModeContextValue = {
    mode,
    isDashboard: mode === 'dashboard',
    isChatbot: mode === 'chatbot',
    toggleMode,
    setMode,
  }

  return (
    <AppModeContext.Provider value={value}>
      {children}
    </AppModeContext.Provider>
  )
}

// ─────────────────────────────────────────
// Custom hook — use this in any component
//
// Usage:
//   const { mode, toggleMode, isDashboard } = useAppMode()
// ─────────────────────────────────────────

export function useAppMode(): AppModeContextValue {
  const ctx = useContext(AppModeContext)
  if (!ctx) {
    throw new Error('useAppMode must be used inside <AppModeProvider>')
  }
  return ctx
}