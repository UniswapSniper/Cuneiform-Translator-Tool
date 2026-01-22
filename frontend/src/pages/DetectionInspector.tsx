import { Card } from '../components/Card'

export default function DetectionInspector() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Detection Inspector</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tablet Image */}
        <div className="lg:col-span-2">
          <Card title="Tablet Viewer">
            <div className="bg-gray-100 aspect-square rounded-lg flex items-center justify-center relative">
              <img
                src="https://via.placeholder.com/600x600?text=Tablet+P100101"
                alt="tablet"
                className="w-full h-full object-cover rounded-lg"
              />
              {/* Overlay detection boxes would go here */}
            </div>
          </Card>
        </div>

        {/* Detection Results */}
        <div>
          <Card title="Detections">
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded cursor-pointer hover:bg-blue-100 transition-colors"
                >
                  <p className="font-medium text-gray-900">Sign {i}</p>
                  <p className="text-sm text-gray-600">Confidence: {(0.9 - i * 0.02).toFixed(2)}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
