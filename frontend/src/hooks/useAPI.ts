import { useState, useEffect } from 'react'
import apiClient from '../lib/api'

interface UseFetchOptions {
  skip?: boolean
}

interface UseFetchResult<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useFetch<T>(
  url: string,
  options?: UseFetchOptions
): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(!options?.skip)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.get<T>(url)
      setData(response.data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!options?.skip) {
      fetchData()
    }
  }, [url, options?.skip])

  return { data, loading, error, refetch: fetchData }
}

export function usePipelineAPI() {
  const startPipeline = async (config: Record<string, any>) => {
    return apiClient.post('/pipeline/start', { config })
  }

  const getPipelineStatus = async (runId: number) => {
    return apiClient.get(`/pipeline/${runId}`)
  }

  const cancelPipeline = async (runId: number) => {
    return apiClient.post(`/pipeline/${runId}/cancel`)
  }

  return { startPipeline, getPipelineStatus, cancelPipeline }
}

export function useModelsAPI() {
  const listModels = async (page = 1) => {
    return apiClient.get('/models', { params: { page } })
  }

  const getModel = async (modelId: number) => {
    return apiClient.get(`/models/${modelId}`)
  }

  const compareModels = async (modelIds: number[]) => {
    return apiClient.post('/models/compare', { model_ids: modelIds })
  }

  return { listModels, getModel, compareModels }
}

export function useTabletsAPI() {
  const listTablets = async (page = 1, search?: string) => {
    return apiClient.get('/tablets', { params: { page, search } })
  }

  const getTablet = async (tabletId: number) => {
    return apiClient.get(`/tablets/${tabletId}`)
  }

  const addAnnotation = async (
    tabletId: number,
    annotation: Record<string, any>
  ) => {
    return apiClient.post(`/tablets/${tabletId}/annotations`, annotation)
  }

  return { listTablets, getTablet, addAnnotation }
}
