import { useEffect, useRef } from 'react'
import { usePipelineStore } from '../stores/websocketStore'

interface LiveLogProps {
  maxLines?: number
  showTimestamps?: boolean
  autoScroll?: boolean
}

export function LiveLog({ maxLines = 50, showTimestamps = true, autoScroll = true }: LiveLogProps) {
  const pipeline = usePipelineStore()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [pipeline.logs, autoScroll])

  const displayLogs = pipeline.logs.slice(-maxLines)

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Logs</h3>
      <div
        ref={scrollRef}
        className="bg-gray-900 text-gray-100 p-4 rounded font-mono text-sm max-h-96 overflow-y-auto space-y-1"
      >
        {displayLogs.length === 0 ? (
          <p className="text-gray-600">Waiting for logs...</p>
        ) : (
          displayLogs.map((log, idx) => {
            const levelColor =
              log.level === 'error'
                ? 'text-red-400'
                : log.level === 'warning'
                  ? 'text-amber-400'
                  : log.level === 'info'
                    ? 'text-blue-400'
                    : 'text-green-400'

            return (
              <div key={idx} className={`flex gap-2 ${levelColor}`}>
                <span className="text-gray-600 flex-shrink-0 w-12">
                  [{log.level.toUpperCase().padEnd(5)}]
                </span>
                {showTimestamps && (
                  <span className="text-gray-600 flex-shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                )}
                <span className="flex-1">{log.message}</span>
              </div>
            )
          })
        )}
      </div>
      {displayLogs.length > 0 && (
        <div className="mt-2 text-xs text-gray-600">
          Showing {displayLogs.length} of {pipeline.logs.length} logs
        </div>
      )}
    </div>
  )
}
