import { useUIStore } from '../../stores/uiStore'
import { useAuthStore } from '../../stores/authStore'
import { Bars3Icon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'

export default function Header() {
  const { toggleSidebar } = useUIStore()
  const { logout } = useAuthStore()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-8 py-4 flex items-center justify-between">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Bars3Icon className="w-6 h-6" />
        </button>

        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
            <BellIcon className="w-6 h-6 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <div className="flex items-center gap-2 pl-4 border-l border-gray-200">
            <UserCircleIcon className="w-8 h-8 text-gray-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">Admin</p>
              <p className="text-xs text-gray-500">System Administrator</p>
            </div>
          </div>

          <button
            onClick={logout}
            className="ml-4 px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
