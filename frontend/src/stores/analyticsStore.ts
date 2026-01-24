import { create } from 'zustand'
import { API_BASE_URL } from '../lib/constants'

export interface AnalyticsData {
  total_pipeline_runs: number
  total_models: number
  total_tablets: number
  total_annotations: number
  average_mAP: number
}

interface AnalyticsStore {
  data: AnalyticsData | null
  loading: boolean
  error: string | null
  lastUpdated: Date | null
  failureCount: number       // Track consecutive failures
  isCircuitOpen: boolean     // Circuit breaker state

  // Actions
  setData: (data: AnalyticsData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLastUpdated: (date: Date) => void
  fetch: () => Promise<void>
  reset: () => void
  resetCircuit: () => void   // Reset circuit breaker
}

const MAX_FAILURES = 3  // Stop trying after 3 consecutive failures

export const useAnalyticsStore = create<AnalyticsStore>((set, get) => ({
  data: null,
  loading: false,
  error: null,
  lastUpdated: null,
  failureCount: 0,
  isCircuitOpen: false,

  setData: (data) => set({ data }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setLastUpdated: (date) => set({ lastUpdated: date }),

  fetch: async () => {
    const state = get()

    // Guard: Don't fetch if API is not configured
    if (!API_BASE_URL) {
      set({ error: 'Backend not configured', loading: false })
      return
    }

    // Circuit breaker: Stop if too many failures
    if (state.isCircuitOpen) {
      return  // Silently skip - don't flood console
    }

    set({ loading: true, error: null })
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/summary`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      set({ data, lastUpdated: new Date(), failureCount: 0 })  // Reset on success
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch analytics'
      const newFailureCount = state.failureCount + 1

      // Open circuit if too many failures
      if (newFailureCount >= MAX_FAILURES) {
        console.warn(`Analytics: Circuit breaker opened after ${MAX_FAILURES} failures`)
        set({ error: message, isCircuitOpen: true, failureCount: newFailureCount })
      } else {
        set({ error: message, failureCount: newFailureCount })
      }
    } finally {
      set({ loading: false })
    }
  },

  reset: () => set({ data: null, error: null, lastUpdated: null }),
  resetCircuit: () => set({ failureCount: 0, isCircuitOpen: false, error: null }),
}))
