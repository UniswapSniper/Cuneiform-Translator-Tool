import { useEffect, useRef } from 'react'
import io, { Socket } from 'socket.io-client'
import { usePipelineStore } from '../stores/pipelineStore'

export function useWebSocket(url?: string) {
  const socketRef = useRef<Socket | null>(null)

  useEffect(() => {
    const socketURL = url || import.meta.env.VITE_SOCKET_URL || 'http://localhost:5001'
    
    socketRef.current = io(socketURL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    })

    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket')
    })

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket')
    })

    return () => {
      socketRef.current?.disconnect()
    }
  }, [url])

  return socketRef.current
}

export function usePipelineWebSocket(runId?: number) {
  const socket = useWebSocket()
  const { updateProgress, updateStatus } = usePipelineStore()

  useEffect(() => {
    if (!socket || !runId) return

    // Subscribe to pipeline updates
    socket.emit('subscribe:pipeline', { run_id: runId })

    // Listen for progress updates
    socket.on('pipeline:progress', (data) => {
      updateProgress(data.progress)
      updateStatus(data.status)
    })

    // Listen for step updates
    socket.on('step:progress', (data) => {
      console.log('Step update:', data)
    })

    // Listen for metrics updates
    socket.on('metrics', (data) => {
      console.log('Metrics update:', data)
    })

    return () => {
      socket.emit('unsubscribe:pipeline', { run_id: runId })
      socket.off('pipeline:progress')
      socket.off('step:progress')
      socket.off('metrics')
    }
  }, [socket, runId, updateProgress, updateStatus])

  return socket
}
