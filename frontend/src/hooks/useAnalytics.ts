import { useEffect, useRef } from 'react'
import { useAnalyticsStore } from '../stores/analyticsStore'
import { IS_BACKEND_CONFIGURED } from '../lib/constants'

export function useAnalytics(refetchInterval: number = 30000) {
  const store = useAnalyticsStore()
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    // Guard: Skip if backend is not configured
    if (!IS_BACKEND_CONFIGURED) {
      return
    }

    // Fetch immediately on mount
    store.fetch()

    // Set up periodic refresh
    intervalRef.current = setInterval(() => {
      store.fetch()
    }, refetchInterval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [store, refetchInterval])

  return store
}
