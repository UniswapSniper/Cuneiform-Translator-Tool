import { motion } from 'framer-motion'

interface ProgressBarProps {
  progress: number
  status?: 'idle' | 'running' | 'completed' | 'failed'
  label?: string
}

export function ProgressBar({
  progress,
  status = 'idle',
  label,
}: ProgressBarProps) {
  const getColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      case 'running':
        return 'bg-blue-500'
      default:
        return 'bg-gray-300'
    }
  }

  return (
    <div className="w-full">
      {label && <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <motion.div
          className={`h-2 rounded-full ${getColor()}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{progress}%</p>
    </div>
  )
}
