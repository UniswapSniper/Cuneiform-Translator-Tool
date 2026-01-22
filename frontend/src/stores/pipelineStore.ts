import { create } from 'zustand'

interface PipelineRun {
  id: number
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
}

interface PipelineStore {
  currentRun: PipelineRun | null
  setCurrentRun: (run: PipelineRun | null) => void
  updateProgress: (progress: number) => void
  updateStatus: (status: PipelineRun['status']) => void
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  currentRun: null,
  setCurrentRun: (run) => set({ currentRun: run }),
  updateProgress: (progress) =>
    set((state) =>
      state.currentRun ? { currentRun: { ...state.currentRun, progress } } : state
    ),
  updateStatus: (status) =>
    set((state) =>
      state.currentRun ? { currentRun: { ...state.currentRun, status } } : state
    ),
}))
