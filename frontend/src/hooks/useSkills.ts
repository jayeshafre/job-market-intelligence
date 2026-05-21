import { useState, useEffect, useCallback } from 'react'
import { fetchSkillsData } from '@/services/skillsService'
import type { SkillsData } from '@/types/skills'
import type { FetchStatus } from '@/types/dashboard'

interface Return {
  data: SkillsData | null
  status: FetchStatus
  error: string | null
  refetch: () => void
}

export function useSkills(): Return {
  const [data, setData]     = useState<SkillsData | null>(null)
  const [status, setStatus] = useState<FetchStatus>('idle')
  const [error, setError]   = useState<string | null>(null)

  const load = useCallback(async () => {
    setStatus('loading')
    setError(null)
    try {
      setData(await fetchSkillsData())
      setStatus('success')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load')
      setStatus('error')
    }
  }, [])

  useEffect(() => { load() }, [load])
  return { data, status, error, refetch: load }
}