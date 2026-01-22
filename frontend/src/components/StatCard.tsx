interface StatProps {
  label: string
  value: string | number
  change?: number
  icon?: React.ReactNode
}

export function StatCard({ label, value, change, icon }: StatProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {change !== undefined && (
            <p
              className={`text-sm font-medium mt-2 ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {change >= 0 ? '+' : ''}{change}% from last month
            </p>
          )}
        </div>
        {icon && <div className="text-3xl">{icon}</div>}
      </div>
    </div>
  )
}
