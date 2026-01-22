import { LiveMetricsChart } from '../components/LiveMetricsChart'
import { MetricsPanel } from '../components/MetricsPanel'
import { LiveLog } from '../components/LiveLog'
import { usePipelineStore } from '../stores/websocketStore'

export default function Analytics() {
  const pipeline = usePipelineStore()
  const isRunning = pipeline.status === 'running'

  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics & Research Hub</h1>

      {isRunning && (
        <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-medium text-blue-900">
            🟢 Live Pipeline Running - Real-time metrics streaming below
          </p>
        </div>
      )}

      {isRunning ? (
        <div className="space-y-8">
          {/* Live Charts */}
          <LiveMetricsChart />

          {/* Current Metrics */}
          <MetricsPanel title="Current Training Metrics" layout="grid" />

          {/* Live Logs */}
          <LiveLog maxLines={100} showTimestamps={true} autoScroll={true} />
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-xl text-gray-600 mb-2">No active pipeline</p>
          <p className="text-gray-500">Start a pipeline from the Pipeline Control page to see live analytics</p>
        </div>
      )}
    </div>
  )
}
