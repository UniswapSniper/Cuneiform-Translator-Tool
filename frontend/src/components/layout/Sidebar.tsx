import { Link, useLocation } from 'react-router-dom'
import { useUIStore } from '../../stores/uiStore'
import {
  HomeIcon,
  PlayIcon,
  SparklesIcon,
  PhotoIcon,
  EyeIcon,
  ChartBarIcon,
  CogIcon,
} from '@heroicons/react/24/outline'

const navItems = [
  { label: 'Dashboard', path: '/', icon: HomeIcon },
  { label: 'Pipeline', path: '/pipeline', icon: PlayIcon },
  { label: 'Models', path: '/models', icon: SparklesIcon },
  { label: 'Tablets', path: '/tablets', icon: PhotoIcon },
  { label: 'Detection', path: '/detection', icon: EyeIcon },
  { label: 'Analytics', path: '/analytics', icon: ChartBarIcon },
  { label: 'Settings', path: '/settings', icon: CogIcon },
]

export default function Sidebar() {
  const location = useLocation()
  const { toggleSidebar } = useUIStore()

  return (
    <aside className="w-64 bg-gray-900 text-white shadow-lg">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">🏛️ Cuneiform</h1>
        <p className="text-sm text-gray-400 mt-1">Sign Translator</p>
      </div>

      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <button
          onClick={toggleSidebar}
          className="w-full px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        >
          Collapse
        </button>
      </div>
    </aside>
  )
}
