import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface TypewriterTextProps {
    text: string
    speed?: number  // ms per character
    className?: string
    onComplete?: () => void
}

export function TypewriterText({
    text,
    speed = 50,
    className = '',
    onComplete
}: TypewriterTextProps) {
    const [displayedText, setDisplayedText] = useState('')
    const [currentIndex, setCurrentIndex] = useState(0)
    const [isComplete, setIsComplete] = useState(false)

    useEffect(() => {
        if (currentIndex < text.length) {
            const timeout = setTimeout(() => {
                setDisplayedText(prev => prev + text[currentIndex])
                setCurrentIndex(prev => prev + 1)
            }, speed)
            return () => clearTimeout(timeout)
        } else if (!isComplete) {
            setIsComplete(true)
            onComplete?.()
        }
    }, [currentIndex, text, speed, isComplete, onComplete])

    // Reset when text changes
    useEffect(() => {
        setDisplayedText('')
        setCurrentIndex(0)
        setIsComplete(false)
    }, [text])

    return (
        <div className={`relative ${className}`}>
            <span className="text-cyan-100">
                {displayedText}
            </span>
            {!isComplete && (
                <motion.span
                    className="inline-block w-0.5 h-5 bg-cyan-400 ml-1"
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ repeat: Infinity, duration: 0.8 }}
                />
            )}
        </div>
    )
}

interface WordByWordTextProps {
    words: string[]
    currentIndex: number
    className?: string
}

export function WordByWordText({ words, currentIndex, className = '' }: WordByWordTextProps) {
    return (
        <div className={`relative ${className}`}>
            <AnimatePresence mode="popLayout">
                {words.slice(0, currentIndex + 1).map((word, idx) => (
                    <motion.span
                        key={`${word}-${idx}`}
                        initial={{ opacity: 0, y: 10, filter: 'blur(4px)' }}
                        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="inline-block mr-2"
                        style={{
                            textShadow: idx === currentIndex
                                ? '0 0 10px rgba(0,212,255,0.8), 0 0 20px rgba(0,212,255,0.5)'
                                : 'none'
                        }}
                    >
                        {word}
                    </motion.span>
                ))}
            </AnimatePresence>
            {currentIndex < words.length - 1 && (
                <motion.span
                    className="inline-block w-0.5 h-5 bg-cyan-400 ml-1"
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ repeat: Infinity, duration: 0.8 }}
                />
            )}
        </div>
    )
}
