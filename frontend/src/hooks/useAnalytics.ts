import { useEffect, useRef } from 'react'
import { useAnalyticsStore } from '../stores/analyticsStore'

export function useAnalytics(refetchInterval: number = 30000) {
  const store = useAnalyticsStore()
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
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
