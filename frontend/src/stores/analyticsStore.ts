import { create } from 'zustand'

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
  
  // Actions
  setData: (data: AnalyticsData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLastUpdated: (date: Date) => void
  fetch: () => Promise<void>
  reset: () => void
}

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  data: null,
  loading: false,
  error: null,
  lastUpdated: null,

  setData: (data) => set({ data }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setLastUpdated: (date) => set({ lastUpdated: date }),

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('http://localhost:5001/api/analytics/summary')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      set({ data, lastUpdated: new Date() })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch analytics'
      set({ error: message })
    } finally {
      set({ loading: false })
    }
  },

  reset: () => set({ data: null, error: null, lastUpdated: null }),
}))
