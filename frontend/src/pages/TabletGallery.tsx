import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../components/Card'
import { TabletUpload } from '../components/TabletUpload'
import { API_BASE_URL } from '../lib/constants'

interface Tablet {
  id: number
  pnumber: string
  name: string
  period: string
  quality_score: number
  annotation_count: number
  thumbnail_path?: string
}

export default function TabletGallery() {
  const navigate = useNavigate()
  const [tablets, setTablets] = useState<Tablet[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [quality, setQuality] = useState('')

  useEffect(() => {
    const fetchTablets = async () => {
      setLoading(true)
      try {
        const query = new URLSearchParams()
        if (search) query.append('search', search)
        if (quality) query.append('quality_status', quality.toLowerCase())

        const response = await fetch(`${API_BASE_URL}/tablets?${query.toString()}`)
        const data = await response.json()
        setTablets(data.items || [])
      } catch (error) {
        console.error('Failed to fetch tablets:', error)
      } finally {
        setLoading(false)
      }
    }

    const timer = setTimeout(fetchTablets, 300)
    return () => clearTimeout(timer)
  }, [search, quality])

  const refreshTablets = () => {
    setSearch(prev => prev + ' ')  // Trigger refetch
    setTimeout(() => setSearch(prev => prev.trim()), 100)
  }

  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Tablet Gallery</h1>

      {/* Upload Section */}
      <div className="mb-8">
        <TabletUpload onUploadSuccess={refreshTablets} />
      </div>

      <div className="mb-6 flex gap-4">
        <input
          type="search"
          placeholder="Search by P-number or name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select
          value={quality}
          onChange={(e) => setQuality(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Quality Levels</option>
          <option value="Pass">Pass</option>
          <option value="Warning">Warning</option>
          <option value="Fail">Fail</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-500">Loading tablets...</div>
      ) : tablets.length === 0 ? (
        <div className="text-center py-20 text-gray-500">No tablets found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tablets.map((tablet) => (
            <Card key={tablet.id} className="cursor-pointer hover:shadow-lg transition-shadow overflow-hidden">
              <div className="bg-gray-100 h-40 rounded-lg mb-4 flex items-center justify-center bg-cover bg-center" style={{ backgroundImage: tablet.thumbnail_path ? `url(${tablet.thumbnail_path})` : 'none' }}>
                {!tablet.thumbnail_path && <span className="text-4xl">📜</span>}
              </div>
              <h3 className="font-semibold text-gray-900">{tablet.pnumber}</h3>
              <p className="text-sm text-gray-600 mt-1">{tablet.name || tablet.period || 'Unknown period'}</p>
              <div className="mt-4 flex items-center justify-between">
                <span className={`text-xs px-2 py-1 rounded-full ${tablet.quality_score > 80 ? 'bg-green-100 text-green-800' :
                  tablet.quality_score > 50 ? 'bg-amber-100 text-amber-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                  Quality: {tablet.quality_score.toFixed(0)}%
                </span>
                <span className="text-xs text-gray-500">{tablet.annotation_count} annotations</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  navigate(`/decode/${tablet.id}`)
                }}
                className="mt-3 w-full py-2 bg-gradient-to-r from-cyan-500 to-purple-500 text-white text-sm font-semibold rounded-lg hover:from-cyan-600 hover:to-purple-600 transition-all shadow-md hover:shadow-lg"
              >
                🔬 Analyze
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
