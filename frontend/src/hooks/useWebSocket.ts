import { useEffect, useRef } from 'react'
import io, { Socket } from 'socket.io-client'
import { usePipelineStore } from '../stores/websocketStore'
import { SOCKET_URL, IS_BACKEND_CONFIGURED } from '../lib/constants'

export function useWebSocket(url?: string) {
  const socketRef = useRef<Socket | null>(null)
  const { setConnected, setConnectionError } = usePipelineStore()

  useEffect(() => {
    const socketURL = url || SOCKET_URL

    // Guard: Don't attempt connection if no valid URL
    if (!socketURL) {
      console.warn('WebSocket: No backend URL configured. Skipping connection.')
      setConnected(false)
      setConnectionError('Backend not configured')
      return
    }

    socketRef.current = io(socketURL, {
      reconnection: true,
      reconnectionDelay: 2000,        // Start with 2 second delay
      reconnectionDelayMax: 30000,    // Max 30 seconds between attempts
      reconnectionAttempts: 3,        // Only try 3 times (reduced from 5)
      timeout: 10000,                 // 10 second timeout
    })

    socketRef.current.on('connect', () => {
      console.log('✅ Connected to WebSocket')
      setConnected(true)
      setConnectionError(null)
    })

    socketRef.current.on('disconnect', () => {
      console.log('❌ Disconnected from WebSocket')
      setConnected(false)
    })

    socketRef.current.on('error', (data: any) => {
      // Use warn instead of error to reduce console noise
      console.warn('WebSocket connection issue:', data?.message || 'Connection error')
      setConnectionError(data?.message || 'WebSocket connection error')
    })

    socketRef.current.on('connect_error', (error: Error) => {
      // Log only once per error type to reduce console spam
      console.warn('WebSocket connect error:', error.message)
      setConnectionError(error.message)
    })

    return () => {
      socketRef.current?.disconnect()
    }
  }, [url, setConnected, setConnectionError])

  return socketRef.current
}

export function usePipelineWebSocket(runId?: number) {
  const socket = useWebSocket()
  const store = usePipelineStore()
  const subscribed = useRef(false)

  useEffect(() => {
    if (!socket || !runId) return

    // Avoid duplicate subscriptions
    if (!subscribed.current) {
      socket.emit('subscribe:pipeline', { run_id: runId })
      subscribed.current = true
      store.setRunId(runId)
    }

    // Pipeline progress updates
    const handlePipelineProgress = (data: any) => {
      store.updateProgress(data.progress)
      store.updateStatus(data.status)
      store.updateStatusMessage(data.message || '')
    }

    // Step progress updates
    const handleStepProgress = (data: any) => {
      store.updateStep(data.step_name, data.progress, data.status)
    }

    // Metrics updates
    const handleMetricsUpdate = (data: any) => {
      store.updateMetrics(data.metrics)
    }

    // Batch metrics updates
    const handleBatchMetrics = (data: any) => {
      store.addBatchMetrics({
        batch_num: data.batch_num,
        epoch: data.epoch,
        metrics: data.metrics,
        timestamp: data.timestamp,
      })
    }

    // Log messages
    const handleLogMessage = (data: any) => {
      store.addLog({
        level: data.level,
        message: data.message,
        timestamp: data.timestamp,
        context: data.context,
      })
    }

    // Error handling
    const handlePipelineError = (data: any) => {
      store.setError(data.error_message, data.traceback)
    }

    // Pipeline lifecycle
    const handlePipelineStarted = (data: any) => {
      console.log('Pipeline started:', data)
      store.updateStatus('running')
      store.updateProgress(0)
    }

    const handlePipelineCompleted = (data: any) => {
      console.log('Pipeline completed:', data)
      store.updateStatus('completed')
      store.updateProgress(100)
    }

    // Register all handlers
    socket.on('pipeline:progress', handlePipelineProgress)
    socket.on('step:progress', handleStepProgress)
    socket.on('metrics:update', handleMetricsUpdate)
    socket.on('batch:metrics', handleBatchMetrics)
    socket.on('log:message', handleLogMessage)
    socket.on('pipeline:error', handlePipelineError)
    socket.on('pipeline:started', handlePipelineStarted)
    socket.on('pipeline:completed', handlePipelineCompleted)

    // Cleanup
    return () => {
      socket.emit('unsubscribe:pipeline', { run_id: runId })
      socket.off('pipeline:progress', handlePipelineProgress)
      socket.off('step:progress', handleStepProgress)
      socket.off('metrics:update', handleMetricsUpdate)
      socket.off('batch:metrics', handleBatchMetrics)
      socket.off('log:message', handleLogMessage)
      socket.off('pipeline:error', handlePipelineError)
      socket.off('pipeline:started', handlePipelineStarted)
      socket.off('pipeline:completed', handlePipelineCompleted)
      subscribed.current = false
    }
  }, [socket, runId, store])

  return socket
}
