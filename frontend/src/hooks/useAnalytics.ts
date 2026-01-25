import { useEffect, useRef } from 'react'
import { useAnalyticsStore } from '../stores/analyticsStore'
import { IS_BACKEND_CONFIGURED } from '../lib/constants'

export function useAnalytics(refetchInterval: number = 30000) {
  // Select specific action to verify stability and prevent infinite loops in useEffect
  const fetch = useAnalyticsStore(state => state.fetch)
  // Get full state to return to component
  const store = useAnalyticsStore()

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    // Guard: Skip if backend is not configured
    if (!IS_BACKEND_CONFIGURED) {
      return
    }

    // Fetch immediately on mount
    fetch()

    // Set up periodic refresh
    intervalRef.current = setInterval(() => {
      fetch()
    }, refetchInterval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetch, refetchInterval])

  return store
}
