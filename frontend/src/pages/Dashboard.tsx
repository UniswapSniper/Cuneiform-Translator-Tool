export default function Dashboard() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Welcome to Cuneiform Translator</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="card">
          <p className="text-gray-600 font-medium">Total Tablets</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">324</p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Models Trained</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">12</p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Pipeline Runs</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">156</p>
        </div>
        <div className="card">
          <p className="text-gray-600 font-medium">Avg mAP Score</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">0.847</p>
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
    </div>
  )
}
