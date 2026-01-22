import { useState } from 'react'
import { usePipelineWebSocket } from '../hooks/useWebSocket'
import { usePipelineStore } from '../stores/websocketStore'

export function WebSocketTest() {
  const [runId, setRunId] = useState<number>(1)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const store = usePipelineStore()
  usePipelineWebSocket(isSubscribed ? runId : undefined)

  const handleStartTest = async () => {
    setIsSubscribed(true)
    setRunId(1)

    // Simulate pipeline events
    try {
      const response = await fetch('http://localhost:5001/api/test/websocket/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: 1,
          num_events: 5,
          event_type: 'progress',
        }),
      })
      const data = await response.json()
      console.log('Test events sent:', data)
    } catch (error) {
      console.error('Failed to start test:', error)
    }
  }

  const handleSendMetrics = async () => {
    try {
      await fetch('http://localhost:5001/api/test/websocket/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: runId,
          num_events: 10,
          event_type: 'batch',
        }),
      })
    } catch (error) {
      console.error('Failed to send metrics:', error)
    }
  }

  const handleStopSubscription = () => {
    setIsSubscribed(false)
    store.reset()
  }

  return (
    <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
      <h3 className="text-lg font-semibold mb-4">WebSocket Connectivity Test</h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white p-3 rounded border">
          <p className="text-sm text-gray-600">Connection Status</p>
          <p className={`text-lg font-bold ${store.connected ? 'text-green-600' : 'text-red-600'}`}>
            {store.connected ? '✅ Connected' : '❌ Disconnected'}
          </p>
        </div>

        <div className="bg-white p-3 rounded border">
          <p className="text-sm text-gray-600">Pipeline Status</p>
          <p className="text-lg font-bold text-blue-600">{store.status.toUpperCase()}</p>
        </div>

        <div className="bg-white p-3 rounded border">
          <p className="text-sm text-gray-600">Overall Progress</p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${store.progress}%` }}
            />
          </div>
          <p className="text-sm font-semibold mt-1">{store.progress}%</p>
        </div>

        <div className="bg-white p-3 rounded border">
          <p className="text-sm text-gray-600">Current Step</p>
          <p className="text-lg font-bold">{store.currentStep || 'None'}</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Status Message</p>
        <p className="text-sm text-gray-800 bg-white p-2 rounded border">
          {store.statusMessage || 'Waiting...'}
        </p>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Metrics</p>
        <div className="bg-white p-2 rounded border text-sm">
          {Object.entries(store.metrics).length > 0 ? (
            <div className="space-y-1">
              {Object.entries(store.metrics).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-600">{key}:</span>
                  <span className="font-semibold">{value?.toFixed(4)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No metrics yet</p>
          )}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Recent Logs ({store.logs.length})</p>
        <div className="bg-white p-2 rounded border text-xs max-h-40 overflow-y-auto space-y-1">
          {store.logs.slice(-10).map((log, idx) => (
            <div key={idx} className={`text-${log.level === 'error' ? 'red' : 'gray'}-700`}>
              <span className="font-semibold">[{log.level.toUpperCase()}]</span> {log.message}
            </div>
          ))}
          {store.logs.length === 0 && <p className="text-gray-500">No logs yet</p>}
        </div>
      </div>

      <div className="space-y-2">
        {!isSubscribed ? (
          <button
            onClick={handleStartTest}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-semibold"
          >
            ▶ Start WebSocket Test
          </button>
        ) : (
          <>
            <button
              onClick={handleSendMetrics}
              className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 font-semibold"
            >
              📊 Send Test Metrics
            </button>
            <button
              onClick={handleStopSubscription}
              className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-semibold"
            >
              ⏹ Stop Test
            </button>
          </>
        )}
      </div>

      {store.connectionError && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 rounded text-red-800">
          <p className="font-semibold">Connection Error</p>
          <p className="text-sm">{store.connectionError}</p>
        </div>
      )}

      {store.lastError && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 rounded text-red-800">
          <p className="font-semibold">Pipeline Error</p>
          <p className="text-sm">{store.lastError}</p>
          {store.errorDetails && <p className="text-xs mt-1 font-mono">{store.errorDetails}</p>}
        </div>
      )}
    </div>
  )
}
