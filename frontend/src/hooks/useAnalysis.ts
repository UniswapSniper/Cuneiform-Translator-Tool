import { useEffect, useRef, useState, useCallback } from 'react'
import io, { Socket } from 'socket.io-client'
import { SOCKET_URL, API_BASE_URL, isApiAvailable } from '../lib/constants'

interface DetectedSign {
    id: number
    name: string
    x: number
    y: number
    width: number
    height: number
    confidence: number
    unicode?: string
}

interface AnalysisState {
    phase: 'idle' | 'scanning' | 'detection' | 'translation' | 'complete'
    scanProgress: number
    detectionProgress: number
    translationProgress: number
    signs: DetectedSign[]
    translationWords: string[]
    currentWordIndex: number
    fullTranslation: string
    translationSource: 'cdli_scholarly' | 'neural_model' | 'sign_dictionary' | 'contextual_placeholder' | 'unknown'
    message: string
    confidence: number
    isConnected: boolean
}

const initialState: AnalysisState = {
    phase: 'idle',
    scanProgress: 0,
    detectionProgress: 0,
    translationProgress: 0,
    signs: [],
    translationWords: [],
    currentWordIndex: -1,
    fullTranslation: '',
    translationSource: 'unknown',
    message: '',
    confidence: 0,
    isConnected: false
}

export function useAnalysis(tabletId: number | undefined) {
    const [state, setState] = useState<AnalysisState>(initialState)
    const socketRef = useRef<Socket | null>(null)

    // Connect to WebSocket and join tablet room
    useEffect(() => {
        if (!tabletId || !SOCKET_URL) return

        socketRef.current = io(SOCKET_URL, {
            reconnection: true,
            timeout: 10000,
        })

        const socket = socketRef.current

        socket.on('connect', () => {
            setState(prev => ({ ...prev, isConnected: true }))
            // Join the tablet-specific room
            socket.emit('join:tablet', { tablet_id: tabletId })
        })

        socket.on('disconnect', () => {
            setState(prev => ({ ...prev, isConnected: false }))
        })

        // Phase change handler
        socket.on('analysis:phase', (data: { phase: string; message: string }) => {
            setState(prev => ({
                ...prev,
                phase: data.phase as AnalysisState['phase'],
                message: data.message
            }))
        })

        // Scanning progress
        socket.on('analysis:scanning', (data: { progress: number }) => {
            setState(prev => ({
                ...prev,
                scanProgress: data.progress
            }))
        })

        // Sign detection
        socket.on('analysis:detection', (data: {
            sign: DetectedSign;
            progress: number;
            sign_index: number;
        }) => {
            setState(prev => ({
                ...prev,
                signs: [...prev.signs, data.sign],
                detectionProgress: data.progress
            }))
        })

        // Translation words
        socket.on('analysis:translation', (data: {
            word: string;
            word_index: number;
            progress: number;
        }) => {
            setState(prev => ({
                ...prev,
                translationWords: [...prev.translationWords, data.word],
                currentWordIndex: data.word_index,
                translationProgress: data.progress
            }))
        })

        // Analysis complete
        socket.on('analysis:complete', (data: {
            translation: string;
            translation_source?: string;
            confidence: number;
            signs_detected: number;
        }) => {
            setState(prev => ({
                ...prev,
                phase: 'complete',
                fullTranslation: data.translation,
                translationSource: (data.translation_source || 'unknown') as AnalysisState['translationSource'],
                confidence: data.confidence
            }))
        })

        return () => {
            socket.emit('leave:tablet', { tablet_id: tabletId })
            socket.disconnect()
        }
    }, [tabletId])

    // Start analysis function
    const startAnalysis = useCallback(async () => {
        if (!tabletId || !isApiAvailable() || !API_BASE_URL) return

        // Reset state
        setState({
            ...initialState,
            isConnected: state.isConnected
        })

        try {
            const response = await fetch(`${API_BASE_URL}/tablets/${tabletId}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })

            if (!response.ok) {
                throw new Error('Failed to start analysis')
            }
        } catch (error) {
            console.error('Failed to start analysis:', error)
            setState(prev => ({
                ...prev,
                phase: 'idle',
                message: 'Failed to start analysis'
            }))
        }
    }, [tabletId, state.isConnected])

    // Reset function
    const reset = useCallback(() => {
        setState(initialState)
    }, [])

    return {
        ...state,
        startAnalysis,
        reset
    }
}
