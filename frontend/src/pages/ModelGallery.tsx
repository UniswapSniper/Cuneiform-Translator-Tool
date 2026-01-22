import { Card } from '../components/Card'

export default function ModelGallery() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Model Gallery</h1>

      <div className="mb-6 flex gap-4">
        <input
          type="search"
          placeholder="Search models..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button className="btn-primary">Train New Model</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="cursor-pointer hover:shadow-lg transition-shadow">
            <div className="bg-gradient-to-br from-blue-100 to-purple-100 h-48 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-4xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Model v{i}</h3>
            <p className="text-sm text-gray-600 mt-1">YOLOv8-m with 3D augmentation</p>
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <div className="bg-gray-50 p-2 rounded">
                <p className="text-gray-600">mAP</p>
                <p className="font-bold text-gray-900">0.{840 + i}</p>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <p className="text-gray-600">Epochs</p>
                <p className="font-bold text-gray-900">{10 + i}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
