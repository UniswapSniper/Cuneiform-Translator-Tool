import { Card } from '../components/Card'

export default function Settings() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Settings & Configuration</h1>

      <div className="max-w-2xl space-y-8">
        {/* API Configuration */}
        <Card title="API Configuration">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Endpoint
              </label>
              <input
                type="url"
                defaultValue="http://localhost:5000/api"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                WebSocket URL
              </label>
              <input
                type="url"
                defaultValue="http://localhost:5000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </Card>

        {/* Training Defaults */}
        <Card title="Training Defaults">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Epochs
              </label>
              <input
                type="number"
                defaultValue="10"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Batch Size
              </label>
              <input
                type="number"
                defaultValue="16"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </Card>

        {/* Data Management */}
        <Card title="Data Management">
          <div className="space-y-4">
            <button className="w-full px-4 py-2 text-left bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors">
              📥 Import Tablets
            </button>
            <button className="w-full px-4 py-2 text-left bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors">
              📤 Export Models
            </button>
            <button className="w-full px-4 py-2 text-left bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors">
              🗑️ Clear Cache
            </button>
          </div>
        </Card>

        {/* Save Button */}
        <div className="flex gap-4">
          <button className="btn-primary">Save Settings</button>
          <button className="btn-secondary">Reset to Defaults</button>
        </div>
      </div>
    </div>
  )
}
