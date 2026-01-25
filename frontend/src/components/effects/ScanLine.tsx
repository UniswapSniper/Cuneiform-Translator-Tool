import { motion } from 'framer-motion'

interface ScanLineProps {
    isActive: boolean
    progress: number  // 0-100
    onComplete?: () => void
}

export function ScanLine({ isActive, progress }: ScanLineProps) {
    if (!isActive) return null

    return (
        <motion.div
            className="absolute left-0 right-0 h-1 pointer-events-none z-20"
            style={{
                top: `${progress}%`,
                background: 'linear-gradient(90deg, transparent 0%, #00d4ff 20%, #00ffff 50%, #00d4ff 80%, transparent 100%)',
                boxShadow: '0 0 20px #00d4ff, 0 0 40px #00d4ff, 0 0 60px rgba(0,212,255,0.5)',
            }}
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{
                opacity: 1,
                scaleX: 1,
            }}
            transition={{ duration: 0.3 }}
        >
            {/* Glow effect above line */}
            <div
                className="absolute -top-8 left-0 right-0 h-8"
                style={{
                    background: 'linear-gradient(to bottom, transparent, rgba(0,212,255,0.3))',
                }}
            />
            {/* Glow effect below line */}
            <div
                className="absolute -bottom-8 left-0 right-0 h-8"
                style={{
                    background: 'linear-gradient(to top, transparent, rgba(0,212,255,0.2))',
                }}
            />
        </motion.div>
    )
}
