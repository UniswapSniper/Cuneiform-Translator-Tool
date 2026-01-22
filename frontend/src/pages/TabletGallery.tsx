import { Card } from '../components/Card'

export default function TabletGallery() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Tablet Gallery</h1>

      <div className="mb-6 flex gap-4">
        <input
          type="search"
          placeholder="Search by P-number or name..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          <option>All Quality Levels</option>
          <option>Pass</option>
          <option>Warning</option>
          <option>Fail</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <Card key={i} className="cursor-pointer hover:shadow-lg transition-shadow overflow-hidden">
            <div className="bg-gray-100 h-40 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-4xl">📜</span>
            </div>
            <h3 className="font-semibold text-gray-900">P10010{i}</h3>
            <p className="text-sm text-gray-600 mt-1">Ur III period</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                Quality: {95 - i}%
              </span>
              <span className="text-xs text-gray-500">{12 + i} annotations</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
