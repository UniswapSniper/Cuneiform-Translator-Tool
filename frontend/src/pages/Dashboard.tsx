import { WebSocketTest } from '../components/WebSocketTest'
import { useAnalytics } from '../hooks/useAnalytics'

export default function Dashboard() {
  const analytics = useAnalytics(30000)

  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Welcome to Cuneiform Translator</h1>
      
      <div className="mb-12 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h2 className="text-lg font-semibold text-blue-900 mb-4">🔧 Phase 2.2: WebSocket Testing</h2>
        <WebSocketTest />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="card">
          <p className="text-gray-600 font-medium">Total Tablets</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {analytics.loading ? '...' : analytics.data?.total_tablets || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Models Trained</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {analytics.loading ? '...' : analytics.data?.total_models || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Pipeline Runs</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {analytics.loading ? '...' : analytics.data?.total_pipeline_runs || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Avg mAP Score</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {analytics.loading ? '...' : analytics.data?.average_mAP.toFixed(3) || '0.000'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Start</h2>
          <div className="space-y-3">
            <button className="w-full btn-primary">Start New Pipeline</button>
            <button className="w-full btn-secondary">Browse Tablets</button>
            <button className="w-full btn-secondary">View Models</button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-4 border-b">
              <span className="text-gray-700">Pipeline run completed</span>
              <span className="text-sm text-gray-500">2 hours ago</span>
            </div>
            <div className="flex items-center justify-between pb-4 border-b">
              <span className="text-gray-700">Model v12 trained</span>
              <span className="text-sm text-gray-500">5 hours ago</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">50 tablets imported</span>
              <span className="text-sm text-gray-500">1 day ago</span>
            </div>
          </div>
        </div>
      </div>

      {analytics.error && (
        <div className="mt-8 p-4 bg-amber-100 border border-amber-400 rounded-lg text-amber-900">
          <p className="font-semibold">⚠️ Analytics Data Error</p>
          <p className="text-sm">{analytics.error}</p>
          <p className="text-xs text-amber-800 mt-1">
            Last updated: {analytics.lastUpdated ? new Date(analytics.lastUpdated).toLocaleTimeString() : 'Never'}
          </p>
        </div>
      )}
    </div>
  )
}
