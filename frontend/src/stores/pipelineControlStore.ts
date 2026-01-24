import { create } from 'zustand'
import { API_BASE_URL, isApiAvailable, reportApiFailure, reportApiSuccess } from '../lib/constants'

export interface PipelineConfig {
  [key: string]: unknown
}

export interface PipelineRun {
  id: number
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  config: PipelineConfig
  created_at: string
  updated_at: string
}

interface PipelineControlStore {
  // Current run
  currentRun: PipelineRun | null
  runs: PipelineRun[]

  // Loading states
  isStarting: boolean
  isCancelling: boolean
  isLoading: boolean
  error: string | null

  // Actions
  setCurrentRun: (run: PipelineRun | null) => void
  setRuns: (runs: PipelineRun[]) => void
  setError: (error: string | null) => void

  // Async actions
  startPipeline: (name: string, config?: PipelineConfig) => Promise<PipelineRun>
  cancelPipeline: (runId: number) => Promise<void>
  fetchRuns: () => Promise<void>
  fetchRunDetails: (runId: number) => Promise<PipelineRun>
  reset: () => void
}



export const usePipelineControlStore = create<PipelineControlStore>((set) => ({
  currentRun: null,
  runs: [],
  isStarting: false,
  isCancelling: false,
  isLoading: false,
  error: null,

  setCurrentRun: (run) => set({ currentRun: run }),
  setRuns: (runs) => set({ runs }),
  setError: (error) => set({ error }),

  startPipeline: async (name, config = {}) => {
    if (!isApiAvailable() || !API_BASE_URL) {
      throw new Error('Backend unavailable')
    }
    set({ isStarting: true, error: null })
    try {
      const response = await fetch(`${API_BASE_URL}/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, config }),
      })

      if (!response.ok) {
        throw new Error(`Failed to start pipeline: ${response.status}`)
      }

      reportApiSuccess()
      const data = await response.json()
      const newRun: PipelineRun = {
        id: data.id,
        name,
        status: 'pending',
        progress: 0,
        config,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      set((state) => ({
        currentRun: newRun,
        runs: [newRun, ...state.runs],
      }))

      return newRun
    } catch (error) {
      reportApiFailure()
      const message = error instanceof Error ? error.message : 'Failed to start pipeline'
      set({ error: message })
      throw error
    } finally {
      set({ isStarting: false })
    }
  },

  cancelPipeline: async (runId) => {
    if (!isApiAvailable() || !API_BASE_URL) {
      throw new Error('Backend unavailable')
    }
    set({ isCancelling: true, error: null })
    try {
      const response = await fetch(`${API_BASE_URL}/pipeline/${runId}/cancel`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`Failed to cancel pipeline: ${response.status}`)
      }

      reportApiSuccess()
      set((state) => ({
        currentRun: state.currentRun?.id === runId
          ? { ...state.currentRun, status: 'cancelled' }
          : state.currentRun,
        runs: state.runs.map((run) =>
          run.id === runId ? { ...run, status: 'cancelled' } : run
        ),
      }))
    } catch (error) {
      reportApiFailure()
      const message = error instanceof Error ? error.message : 'Failed to cancel pipeline'
      set({ error: message })
      throw error
    } finally {
      set({ isCancelling: false })
    }
  },

  fetchRuns: async () => {
    if (!isApiAvailable() || !API_BASE_URL) {
      set({ error: 'Backend unavailable' })
      return
    }
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`${API_BASE_URL}/pipeline/status`)

      if (!response.ok) {
        throw new Error(`Failed to fetch runs: ${response.status}`)
      }

      reportApiSuccess()
      const data = await response.json()
      set({ runs: data.items || [] })
    } catch (error) {
      reportApiFailure()
      const message = error instanceof Error ? error.message : 'Failed to fetch runs'
      set({ error: message })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchRunDetails: async (runId) => {
    if (!isApiAvailable() || !API_BASE_URL) {
      throw new Error('Backend unavailable')
    }
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`${API_BASE_URL}/pipeline/${runId}`)

      if (!response.ok) {
        throw new Error(`Failed to fetch run details: ${response.status}`)
      }

      reportApiSuccess()
      const data = await response.json()
      const run = data.pipeline as PipelineRun
      set({ currentRun: run })
      return run
    } catch (error) {
      reportApiFailure()
      const message = error instanceof Error ? error.message : 'Failed to fetch run details'
      set({ error: message })
      throw error
    } finally {
      set({ isLoading: false })
    }
  },

  reset: () =>
    set({
      currentRun: null,
      runs: [],
      isStarting: false,
      isCancelling: false,
      isLoading: false,
      error: null,
    }),
}))
