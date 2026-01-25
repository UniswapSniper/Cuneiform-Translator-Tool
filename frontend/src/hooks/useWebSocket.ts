import { useEffect, useRef } from 'react'
import io, { Socket } from 'socket.io-client'
import { usePipelineStore } from '../stores/websocketStore'
import { SOCKET_URL, isApiAvailable, reportApiFailure } from '../lib/constants'

// Track if we've already tried to connect and failed
let hasAttemptedConnection = false
let connectionFailed = false

export function useWebSocket(url?: string) {
  const socketRef = useRef<Socket | null>(null)
  const { setConnected, setConnectionError } = usePipelineStore()

  useEffect(() => {
    const socketURL = url || SOCKET_URL

    // Guard: Don't attempt connection if no valid URL
    if (!socketURL) {
      setConnected(false)
      setConnectionError('Backend not configured')
      return
    }

    // Guard: Don't retry if previous connection already failed
    if (connectionFailed || !isApiAvailable()) {
      setConnected(false)
      setConnectionError('Backend unavailable')
      return
    }

    // Guard: Only attempt connection once per page load
    if (hasAttemptedConnection && socketRef.current === null) {
      setConnected(false)
      return
    }

    hasAttemptedConnection = true

    socketRef.current = io(socketURL, {
      reconnection: false,        // DISABLE reconnection entirely
      timeout: 5000,              // 5 second timeout (shorter)
      autoConnect: true,
    })

    socketRef.current.on('connect', () => {
      setConnected(true)
      setConnectionError(null)
    })

    socketRef.current.on('disconnect', () => {
      setConnected(false)
    })

    socketRef.current.on('error', () => {
      connectionFailed = true
      reportApiFailure()
      setConnectionError('WebSocket connection error')
    })

    socketRef.current.on('connect_error', () => {
      connectionFailed = true
      reportApiFailure()
      setConnected(false)
      setConnectionError('Connection failed')
      // Disconnect immediately to prevent retries
      socketRef.current?.disconnect()
      socketRef.current = null
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
  const lastSubscribedId = useRef<number | null>(null)

  useEffect(() => {
    if (!socket || !runId) return

    // Avoid duplicate subscriptions for the SAME runId
    if (lastSubscribedId.current !== runId) {
      if (lastSubscribedId.current !== null) {
        socket.emit('unsubscribe:pipeline', { run_id: lastSubscribedId.current })
      }

      console.log(`Subscribing to pipeline:${runId}`)
      socket.emit('subscribe:pipeline', { run_id: runId })
      lastSubscribedId.current = runId
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
      lastSubscribedId.current = null
    }
  }, [socket, runId, store])

  return socket
}
