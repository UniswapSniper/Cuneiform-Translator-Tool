import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'

export default function PipelineControl() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Pipeline Control</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Control Panel */}
        <div className="lg:col-span-1">
          <Card title="Pipeline Configuration">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model Size
                </label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Nano (n)</option>
                  <option>Small (s)</option>
                  <option selected>Medium (m)</option>
                  <option>Large (l)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Epochs
                </label>
                <input
                  type="number"
                  defaultValue="10"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Batch Size
                </label>
                <input
                  type="number"
                  defaultValue="16"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <label className="flex items-center gap-3">
                <input type="checkbox" className="w-4 h-4 text-blue-600" defaultChecked />
                <span className="text-sm text-gray-700">Enable 3D Augmentation</span>
              </label>

              <button className="w-full btn-primary">
                Start Pipeline
              </button>
            </div>
          </Card>
        </div>

        {/* Status Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Current Run Status">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4">
                  Download Tablets
                </h3>
                <ProgressBar progress={100} status="completed" />
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4">
                  Quality Validation
                </h3>
                <ProgressBar progress={100} status="completed" />
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4">
                  Model Training
                </h3>
                <ProgressBar progress={65} status="running" />
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4">
                  Evaluation
                </h3>
                <ProgressBar progress={0} status="idle" />
              </div>
            </div>
          </Card>

          <Card title="Training Metrics">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Loss</p>
                <p className="text-2xl font-bold text-blue-600">0.243</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">mAP</p>
                <p className="text-2xl font-bold text-green-600">0.847</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
