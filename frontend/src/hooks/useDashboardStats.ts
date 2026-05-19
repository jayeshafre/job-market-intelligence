import { useState, useEffect, useCallback } from 'react'
import { fetchDashboardData } from '@/services/analyticsService'
import type { DashboardData, FetchStatus } from '@/types/dashboard'

// ─────────────────────────────────────────
// useDashboardStats
//
// Fetches all Main Dashboard data in one call.
// Returns data + status + error + a refetch fn.
//
// Usage in MainDashboard.tsx:
//   const { data, status, error, refetch } = useDashboardStats()
// ─────────────────────────────────────────

interface UseDashboardStatsReturn {
  data: DashboardData | null
  status: FetchStatus
  error: string | null
  refetch: () => void
}

export function useDashboardStats(): UseDashboardStatsReturn {
  const [data, setData]     = useState<DashboardData | null>(null)
  const [status, setStatus] = useState<FetchStatus>('idle')
  const [error, setError]   = useState<string | null>(null)

  const load = useCallback(async () => {
    setStatus('loading')
    setError(null)
    try {
      const result = await fetchDashboardData()
      setData(result)
      setStatus('success')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load dashboard data'
      setError(msg)
      setStatus('error')
    }
  }, [])

  // Auto-fetch on mount
  useEffect(() => {
    load()
  }, [load])

  return { data, status, error, refetch: load }
}