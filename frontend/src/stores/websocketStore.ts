import { create } from 'zustand'

interface PipelineMetrics {
  loss?: number
  accuracy?: number
  mAP?: number
  [key: string]: number | undefined
}

interface LogMessage {
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  timestamp: string
  context?: Record<string, unknown>
}

interface PipelineState {
  // Connection state
  connected: boolean
  connectionError: string | null
  
  // Pipeline state
  currentRunId: number | null
  progress: number
  status: 'idle' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
  statusMessage: string
  
  // Step tracking
  currentStep: string | null
  stepProgress: number
  stepStatus: 'pending' | 'running' | 'completed' | 'failed'
  
  // Metrics tracking
  metrics: PipelineMetrics
  batchMetrics: Array<{
    batch_num: number
    epoch: number
    metrics: PipelineMetrics
    timestamp: string
  }>
  
  // Logs
  logs: LogMessage[]
  
  // Errors
  lastError: string | null
  errorDetails: string | null
  
  // Actions
  setConnected: (connected: boolean) => void
  setConnectionError: (error: string | null) => void
  setRunId: (runId: number | null) => void
  updateProgress: (progress: number) => void
  updateStatus: (status: PipelineState['status']) => void
  updateStatusMessage: (message: string) => void
  updateStep: (step: string, progress: number, status: PipelineState['stepStatus']) => void
  updateMetrics: (metrics: PipelineMetrics) => void
  addBatchMetrics: (batch: PipelineState['batchMetrics'][0]) => void
  addLog: (log: LogMessage) => void
  setError: (message: string, details?: string) => void
  clearLogs: () => void
  reset: () => void
}

export const usePipelineStore = create<PipelineState>((set) => ({
  // Initial state
  connected: false,
  connectionError: null,
  currentRunId: null,
  progress: 0,
  status: 'idle',
  statusMessage: '',
  currentStep: null,
  stepProgress: 0,
  stepStatus: 'pending',
  metrics: {},
  batchMetrics: [],
  logs: [],
  lastError: null,
  errorDetails: null,

  // Actions
  setConnected: (connected) => set({ connected }),
  setConnectionError: (error) => set({ connectionError: error }),
  setRunId: (runId) => set({ currentRunId: runId }),
  updateProgress: (progress) => set({ progress }),
  updateStatus: (status) => set({ status }),
  updateStatusMessage: (message) => set({ statusMessage: message }),
  
  updateStep: (step, progress, status) =>
    set({ currentStep: step, stepProgress: progress, stepStatus: status }),
  
  updateMetrics: (metrics) =>
    set((state) => ({ metrics: { ...state.metrics, ...metrics } })),
  
  addBatchMetrics: (batch) =>
    set((state) => ({
      batchMetrics: [...state.batchMetrics.slice(-99), batch], // Keep last 100 batches
    })),
  
  addLog: (log) =>
    set((state) => ({
      logs: [...state.logs.slice(-999), log], // Keep last 1000 logs
    })),
  
  setError: (message, details) =>
    set({ lastError: message, errorDetails: details || null }),
  
  clearLogs: () => set({ logs: [] }),
  
  reset: () =>
    set({
      currentRunId: null,
      progress: 0,
      status: 'idle',
      statusMessage: '',
      currentStep: null,
      stepProgress: 0,
      stepStatus: 'pending',
      metrics: {},
      batchMetrics: [],
      logs: [],
      lastError: null,
      errorDetails: null,
    }),
}))
