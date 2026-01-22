import { usePipelineStore } from '../stores/websocketStore'

interface MetricsPanelProps {
  title?: string
  layout?: 'horizontal' | 'vertical' | 'grid'
}

export function MetricsPanel({ title = 'Metrics', layout = 'grid' }: MetricsPanelProps) {
  const pipeline = usePipelineStore()

  if (Object.keys(pipeline.metrics).length === 0) {
    return (
      <div className="p-4 bg-gray-50 rounded border border-gray-200 text-center text-gray-500">
        Waiting for metrics...
      </div>
    )
  }

  const entries = Object.entries(pipeline.metrics)

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      {layout === 'horizontal' && (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {entries.map(([key, value]) => (
            <div
              key={key}
              className="flex-shrink-0 bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 min-w-40"
            >
              <p className="text-xs font-medium text-blue-700 uppercase tracking-wide">{key}</p>
              <p className="text-2xl font-bold text-blue-900 mt-1">
                {typeof value === 'number' ? value.toFixed(4) : value}
              </p>
            </div>
          ))}
        </div>
      )}

      {layout === 'vertical' && (
        <div className="space-y-3">
          {entries.map(([key, value]) => (
            <div
              key={key}
              className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
            >
              <span className="text-sm font-medium text-gray-700">{key}</span>
              <span className="text-lg font-bold text-gray-900">
                {typeof value === 'number' ? value.toFixed(4) : value}
              </span>
            </div>
          ))}
        </div>
      )}

      {layout === 'grid' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {entries.map(([key, value]) => (
            <div
              key={key}
              className="bg-gradient-to-br from-purple-50 to-purple-100 p-3 rounded-lg border border-purple-200"
            >
              <p className="text-xs font-medium text-purple-700 uppercase truncate">{key}</p>
              <p className="text-xl font-bold text-purple-900 mt-1">
                {typeof value === 'number' ? value.toFixed(3) : value}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
