import { useState, useEffect, useCallback } from 'react'
import { fetchSalaryData } from '@/services/salaryService'
import type { SalaryData } from '@/types/salary'
import type { FetchStatus } from '@/types/dashboard'

interface Return {
  data: SalaryData | null
  status: FetchStatus
  error: string | null
  refetch: () => void
}

export function useSalary(): Return {
  const [data, setData]     = useState<SalaryData | null>(null)
  const [status, setStatus] = useState<FetchStatus>('idle')
  const [error, setError]   = useState<string | null>(null)

  const load = useCallback(async () => {
    setStatus('loading')
    setError(null)
    try {
      setData(await fetchSalaryData())
      setStatus('success')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load')
      setStatus('error')
    }
  }, [])

  useEffect(() => { load() }, [load])
  return { data, status, error, refetch: load }
}