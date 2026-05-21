import { useState, useEffect, useCallback } from 'react'
import { fetchAiImpactData } from '@/services/aiImpactService'
import type { AiImpactData } from '@/types/aiImpact'
import type { FetchStatus } from '@/types/dashboard'

interface Return {
  data: AiImpactData | null
  status: FetchStatus
  error: string | null
  refetch: () => void
}

export function useAiImpact(): Return {
  const [data, setData]     = useState<AiImpactData | null>(null)
  const [status, setStatus] = useState<FetchStatus>('idle')
  const [error, setError]   = useState<string | null>(null)

  const load = useCallback(async () => {
    setStatus('loading')
    setError(null)
    try {
      setData(await fetchAiImpactData())
      setStatus('success')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load')
      setStatus('error')
    }
  }, [])

  useEffect(() => { load() }, [load])
  return { data, status, error, refetch: load }
}