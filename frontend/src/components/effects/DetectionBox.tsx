import { motion } from 'framer-motion'

interface DetectedSign {
    id: number
    name: string
    x: number      // 0-1 percentage
    y: number      // 0-1 percentage
    width: number  // 0-1 percentage
    height: number // 0-1 percentage
    confidence: number
    unicode?: string
}

interface DetectionBoxProps {
    sign: DetectedSign
    index: number
    isHighlighted?: boolean
    onClick?: () => void
}

export function DetectionBox({ sign, index, isHighlighted, onClick }: DetectionBoxProps) {
    return (
        <motion.div
            className="absolute cursor-pointer group"
            style={{
                left: `${sign.x * 100}%`,
                top: `${sign.y * 100}%`,
                width: `${sign.width * 100}%`,
                height: `${sign.height * 100}%`,
            }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{
                opacity: 1,
                scale: 1,
                boxShadow: isHighlighted
                    ? '0 0 20px #00ffff, 0 0 40px #00ffff, 0 0 60px #00ffff'
                    : '0 0 10px #00d4ff, 0 0 20px rgba(0,212,255,0.5)'
            }}
            transition={{
                delay: index * 0.1,
                duration: 0.4,
                type: 'spring',
                stiffness: 200
            }}
            whileHover={{
                scale: 1.05,
                boxShadow: '0 0 25px #00ffff, 0 0 50px #00ffff'
            }}
            onClick={onClick}
        >
            {/* Border with animation */}
            <div
                className="absolute inset-0 border-2 rounded"
                style={{
                    borderColor: isHighlighted ? '#00ffff' : '#00d4ff',
                    animation: 'pulse-glow 2s ease-in-out infinite',
                }}
            />

            {/* Corner accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-cyan-400" />
            <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-cyan-400" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-cyan-400" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-cyan-400" />

            {/* Label */}
            <motion.div
                className="absolute -top-6 left-0 bg-gray-900/90 text-cyan-400 text-xs px-2 py-0.5 rounded whitespace-nowrap"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.2 }}
            >
                <span className="font-mono mr-1">{sign.unicode}</span>
                <span>{sign.name}</span>
                <span className="text-cyan-600 ml-1">({(sign.confidence * 100).toFixed(0)}%)</span>
            </motion.div>
        </motion.div>
    )
}

// CSS for pulse animation (add to global styles)
export const detectionBoxStyles = `
@keyframes pulse-glow {
  0%, 100% { 
    box-shadow: 0 0 10px #00d4ff, 0 0 20px rgba(0,212,255,0.5);
    opacity: 1;
  }
  50% { 
    box-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff;
    opacity: 0.8;
  }
}
`
