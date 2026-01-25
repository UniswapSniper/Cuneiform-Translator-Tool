import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ScanLine } from '../components/effects/ScanLine'
import { DetectionBox } from '../components/effects/DetectionBox'
import { ParticleSystem } from '../components/effects/ParticleSystem'
import { WordByWordText } from '../components/effects/TypewriterText'
import { useAnalysis } from '../hooks/useAnalysis'
import { useSoundEffects } from '../lib/soundEffects'
import { API_BASE_URL } from '../lib/constants'

interface Tablet {
    id: number
    pnumber: string
    name: string
    image_path: string
    period: string
}

export default function DecodingInspector() {
    const { tabletId } = useParams<{ tabletId: string }>()
    const navigate = useNavigate()
    const [tablet, setTablet] = useState<Tablet | null>(null)
    const [highlightedSign, setHighlightedSign] = useState<number | null>(null)
    const prevPhaseRef = useRef<string>('idle')
    const prevSignCountRef = useRef<number>(0)
    const prevWordCountRef = useRef<number>(0)

    const analysis = useAnalysis(tabletId ? parseInt(tabletId) : undefined)
    const sound = useSoundEffects()

    // Play sounds on phase/progress changes
    useEffect(() => {
        // Phase change sounds
        if (analysis.phase !== prevPhaseRef.current) {
            if (analysis.phase === 'complete') {
                sound.playCompleteSound()
            }
            prevPhaseRef.current = analysis.phase
        }

        // Scan beeps (every 10%)
        if (analysis.phase === 'scanning' && analysis.scanProgress % 10 === 0 && analysis.scanProgress > 0) {
            sound.playScanBeep()
        }

        // Detection sounds (on new sign)
        if (analysis.signs.length > prevSignCountRef.current) {
            sound.playDetectSound()
            prevSignCountRef.current = analysis.signs.length
        }

        // Translation sounds (on new word)
        if (analysis.translationWords.length > prevWordCountRef.current) {
            sound.playTranslateSound()
            prevWordCountRef.current = analysis.translationWords.length
        }
    }, [analysis.phase, analysis.scanProgress, analysis.signs.length, analysis.translationWords.length])

    // Fetch tablet details
    useEffect(() => {
        if (!tabletId || !API_BASE_URL) return

        fetch(`${API_BASE_URL}/tablets/${tabletId}`)
            .then(res => res.json())
            .then(data => setTablet(data.tablet))
            .catch(err => console.error('Failed to fetch tablet:', err))
    }, [tabletId])

    const getPhaseColor = () => {
        switch (analysis.phase) {
            case 'scanning': return 'text-cyan-400'
            case 'detection': return 'text-blue-400'
            case 'translation': return 'text-purple-400'
            case 'complete': return 'text-green-400'
            default: return 'text-gray-400'
        }
    }

    const getOverallProgress = () => {
        switch (analysis.phase) {
            case 'scanning': return Math.round(analysis.scanProgress * 0.33)
            case 'detection': return 33 + Math.round(analysis.detectionProgress * 0.33)
            case 'translation': return 66 + Math.round(analysis.translationProgress * 0.34)
            case 'complete': return 100
            default: return 0
        }
    }

    return (
        <div className="min-h-screen bg-gray-950 text-white">
            {/* Ambient background */}
            <div
                className="fixed inset-0 opacity-20"
                style={{
                    backgroundImage: `
            radial-gradient(circle at 20% 50%, rgba(0,212,255,0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 50%, rgba(147,51,234,0.1) 0%, transparent 50%)
          `
                }}
            />

            {/* Grid overlay */}
            <div
                className="fixed inset-0 opacity-5"
                style={{
                    backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
                    backgroundSize: '50px 50px'
                }}
            />

            {/* Floating particles */}
            <ParticleSystem isActive={analysis.phase !== 'idle'} intensity="medium" />

            <div className="relative z-10 p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <button
                        onClick={() => navigate('/tablets')}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                    >
                        ← Back to Gallery
                    </button>

                    <div className="text-center">
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            DECODING INSPECTOR
                        </h1>
                        <p className="text-sm text-gray-500">
                            {tablet?.pnumber} • {tablet?.period || 'Unknown Period'}
                        </p>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Sound toggle */}
                        <button
                            onClick={sound.toggleSound}
                            className={`px-3 py-1 rounded-full text-xs flex items-center gap-1 transition-colors ${sound.enabled
                                    ? 'bg-cyan-900/50 text-cyan-400 border border-cyan-700'
                                    : 'bg-gray-800 text-gray-500 border border-gray-700'
                                }`}
                        >
                            {sound.enabled ? '🔊' : '🔇'} Sound
                        </button>

                        <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${analysis.isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                            <span className="text-xs text-gray-500">
                                {analysis.isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Main content */}
                <div className="grid grid-cols-12 gap-6 h-[calc(100vh-150px)]">

                    {/* Left panel - Detected Signs */}
                    <div className="col-span-2 bg-gray-900/50 rounded-xl border border-gray-800 p-4 overflow-y-auto">
                        <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
                            Detected Signs
                        </h3>
                        <div className="space-y-2">
                            <AnimatePresence>
                                {analysis.signs.map((sign, idx) => (
                                    <motion.div
                                        key={sign.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className={`p-2 rounded-lg cursor-pointer transition-colors ${highlightedSign === sign.id
                                            ? 'bg-cyan-900/50 border border-cyan-500'
                                            : 'bg-gray-800/50 hover:bg-gray-700/50'
                                            }`}
                                        onClick={() => setHighlightedSign(sign.id)}
                                    >
                                        <div className="flex items-center gap-2">
                                            <span className="text-2xl">{sign.unicode}</span>
                                            <div>
                                                <p className="text-sm font-medium">{sign.name}</p>
                                                <p className="text-xs text-gray-500">
                                                    {(sign.confidence * 100).toFixed(0)}% conf
                                                </p>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                            {analysis.signs.length === 0 && analysis.phase === 'idle' && (
                                <p className="text-gray-600 text-sm italic">
                                    Signs will appear here during analysis
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Center - Tablet Image with overlays */}
                    <div className="col-span-6 relative bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden">
                        {/* Tablet image */}
                        {tablet && (
                            <div className="relative w-full h-full flex items-center justify-center p-8">
                                <div className="relative max-w-full max-h-full">
                                    <img
                                        src={tablet.image_path.startsWith('http')
                                            ? tablet.image_path
                                            : `${API_BASE_URL?.replace('/api', '')}${tablet.image_path}`
                                        }
                                        alt={tablet.name}
                                        className="max-w-full max-h-[60vh] rounded-lg shadow-2xl"
                                        style={{
                                            filter: analysis.phase === 'scanning'
                                                ? 'brightness(1.1)'
                                                : 'brightness(1)'
                                        }}
                                    />

                                    {/* Overlay container for effects */}
                                    <div className="absolute inset-0">
                                        {/* Scan line */}
                                        <ScanLine
                                            isActive={analysis.phase === 'scanning'}
                                            progress={analysis.scanProgress}
                                        />

                                        {/* Detection boxes */}
                                        {analysis.phase !== 'idle' && analysis.phase !== 'scanning' && (
                                            analysis.signs.map((sign, idx) => (
                                                <DetectionBox
                                                    key={sign.id}
                                                    sign={sign}
                                                    index={idx}
                                                    isHighlighted={highlightedSign === sign.id}
                                                    onClick={() => setHighlightedSign(sign.id)}
                                                />
                                            ))
                                        )}
                                    </div>

                                    {/* Ambient glow around tablet */}
                                    <div
                                        className="absolute -inset-4 rounded-xl pointer-events-none"
                                        style={{
                                            background: analysis.phase !== 'idle'
                                                ? 'radial-gradient(ellipse at center, rgba(0,212,255,0.1) 0%, transparent 70%)'
                                                : 'none',
                                            transition: 'background 0.5s ease'
                                        }}
                                    />
                                </div>
                            </div>
                        )}

                        {/* Start button overlay */}
                        {analysis.phase === 'idle' && (
                            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50">
                                <motion.button
                                    onClick={analysis.startAnalysis}
                                    className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-xl font-bold text-lg shadow-lg"
                                    whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(0,212,255,0.5)' }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    🔬 Begin Analysis
                                </motion.button>
                            </div>
                        )}
                    </div>

                    {/* Right panel - Translation & Progress */}
                    <div className="col-span-4 space-y-4">
                        {/* Progress section */}
                        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
                            <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
                                Analysis Progress
                            </h3>

                            {/* Overall progress ring */}
                            <div className="flex items-center gap-4 mb-4">
                                <div className="relative w-16 h-16">
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle
                                            cx="32" cy="32" r="28"
                                            fill="none"
                                            stroke="#1f2937"
                                            strokeWidth="4"
                                        />
                                        <circle
                                            cx="32" cy="32" r="28"
                                            fill="none"
                                            stroke="url(#progressGradient)"
                                            strokeWidth="4"
                                            strokeDasharray={`${getOverallProgress() * 1.76} 176`}
                                            strokeLinecap="round"
                                        />
                                        <defs>
                                            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                                <stop offset="0%" stopColor="#00d4ff" />
                                                <stop offset="100%" stopColor="#9333ea" />
                                            </linearGradient>
                                        </defs>
                                    </svg>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="text-sm font-bold">{getOverallProgress()}%</span>
                                    </div>
                                </div>
                                <div>
                                    <p className={`font-semibold ${getPhaseColor()}`}>
                                        {analysis.phase === 'idle' ? 'Ready' : analysis.phase.charAt(0).toUpperCase() + analysis.phase.slice(1)}
                                    </p>
                                    <p className="text-sm text-gray-500">{analysis.message || 'Awaiting command'}</p>
                                </div>
                            </div>

                            {/* Phase indicators */}
                            <div className="space-y-2">
                                {['scanning', 'detection', 'translation'].map((phase, idx) => {
                                    const isActive = analysis.phase === phase
                                    const isComplete = ['scanning', 'detection', 'translation'].indexOf(analysis.phase) > idx || analysis.phase === 'complete'
                                    const progress = phase === 'scanning' ? analysis.scanProgress
                                        : phase === 'detection' ? analysis.detectionProgress
                                            : analysis.translationProgress

                                    return (
                                        <div key={phase} className="flex items-center gap-3">
                                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${isComplete ? 'bg-green-500' : isActive ? 'bg-cyan-500 animate-pulse' : 'bg-gray-700'
                                                }`}>
                                                {isComplete ? '✓' : idx + 1}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="capitalize">{phase}</span>
                                                    <span>{isActive || isComplete ? `${progress}%` : '—'}</span>
                                                </div>
                                                <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                                                    <motion.div
                                                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${isActive || isComplete ? progress : 0}%` }}
                                                        transition={{ duration: 0.3 }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Translation output */}
                        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4 flex-1">
                            <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
                                Translation
                            </h3>

                            <div className="min-h-[200px]">
                                {analysis.translationWords.length > 0 ? (
                                    <WordByWordText
                                        words={analysis.translationWords}
                                        currentIndex={analysis.currentWordIndex}
                                        className="text-lg leading-relaxed"
                                    />
                                ) : (
                                    <p className="text-gray-600 italic">
                                        {analysis.phase === 'idle'
                                            ? 'Translation will appear here after analysis'
                                            : 'Waiting for translation phase...'}
                                    </p>
                                )}
                            </div>

                            {analysis.phase === 'complete' && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-4 p-3 bg-green-900/30 border border-green-700 rounded-lg"
                                >
                                    <div className="flex items-center gap-2 text-green-400">
                                        <span className="text-xl">✨</span>
                                        <span className="font-semibold">Analysis Complete!</span>
                                    </div>
                                    <p className="text-sm text-gray-400 mt-1">
                                        Confidence: {(analysis.confidence * 100).toFixed(1)}%
                                    </p>
                                </motion.div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* CSS for animations */}
            <style>{`
        @keyframes pulse-glow {
          0%, 100% { 
            box-shadow: 0 0 10px #00d4ff, 0 0 20px rgba(0,212,255,0.5);
          }
          50% { 
            box-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff;
          }
        }
      `}</style>
        </div>
    )
}
