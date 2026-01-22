import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { usePipelineStore } from '../stores/websocketStore'

export function LiveMetricsChart() {
  const pipeline = usePipelineStore()

  if (pipeline.batchMetrics.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-gray-50 rounded border border-gray-200">
        <p className="text-gray-500">No metrics data yet. Start a pipeline to see live charts.</p>
      </div>
    )
  }

  // Prepare data for loss chart
  const lossData = pipeline.batchMetrics.map((m, idx) => ({
    batch: idx + 1,
    loss: m.metrics.loss || 0,
    epoch: m.epoch,
  }))

  // Prepare data for accuracy chart
  const accuracyData = pipeline.batchMetrics.map((m, idx) => ({
    batch: idx + 1,
    accuracy: (m.metrics.accuracy || 0) * 100,
    epoch: m.epoch,
  }))

  return (
    <div className="space-y-6">
      {/* Loss Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Training Loss</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={lossData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="batch" />
            <YAxis />
            <Tooltip 
              formatter={(value) => typeof value === 'number' ? value.toFixed(4) : value}
              labelFormatter={(label) => `Batch ${label}`}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="loss" 
              stroke="#ef4444" 
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Accuracy Chart */}
      {accuracyData.some((d) => d.accuracy > 0) && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Accuracy</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="batch" />
              <YAxis domain={[0, 100]} />
              <Tooltip
                formatter={(value) => typeof value === 'number' ? value.toFixed(2) + '%' : value}
                labelFormatter={(label) => `Batch ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#10b981"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* mAP Chart */}
      {pipeline.metrics.mAP && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Mean Average Precision (mAP)</h3>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <p className="text-sm text-gray-600 mb-2">Current mAP</p>
              <p className="text-4xl font-bold text-blue-600">{(pipeline.metrics.mAP as number).toFixed(4)}</p>
            </div>
            <div className="flex-1">
              <div className="relative h-40 bg-gradient-to-t from-blue-100 to-blue-50 rounded border border-blue-200 flex items-end justify-center p-2">
                <div 
                  className="w-8 bg-blue-600 rounded-t transition-all"
                  style={{ height: `${Math.min((pipeline.metrics.mAP as number) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(pipeline.metrics).map(([key, value]) => (
            <div key={key} className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-lg border border-gray-200">
              <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">{key}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {typeof value === 'number' ? value.toFixed(4) : value}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
