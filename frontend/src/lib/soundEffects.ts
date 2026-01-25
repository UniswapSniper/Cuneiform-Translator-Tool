import { useState } from 'react'

// Sound effects for the decoding experience
// Toggle-able via user preference stored in localStorage

// Web Audio API for generating sounds programmatically
class SoundGenerator {
    private audioContext: AudioContext | null = null
    private enabled: boolean = true

    constructor() {
        this.enabled = this.getEnabledState()
    }

    private getContext(): AudioContext {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        }
        return this.audioContext
    }

    private getEnabledState(): boolean {
        if (typeof window === 'undefined') return false
        const stored = localStorage.getItem('soundEffectsEnabled')
        return stored === null ? true : stored === 'true'
    }

    setEnabled(enabled: boolean) {
        this.enabled = enabled
        if (typeof window !== 'undefined') {
            localStorage.setItem('soundEffectsEnabled', String(enabled))
        }
    }

    isEnabled(): boolean {
        return this.enabled
    }

    // Scanning beep - short high-frequency pulse
    playScanBeep() {
        if (!this.enabled) return
        const ctx = this.getContext()
        const oscillator = ctx.createOscillator()
        const gainNode = ctx.createGain()

        oscillator.connect(gainNode)
        gainNode.connect(ctx.destination)

        oscillator.type = 'sine'
        oscillator.frequency.setValueAtTime(1200, ctx.currentTime)
        oscillator.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.1)

        gainNode.gain.setValueAtTime(0.1, ctx.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1)

        oscillator.start(ctx.currentTime)
        oscillator.stop(ctx.currentTime + 0.1)
    }

    // Detection sound - soft ascending tone
    playDetectSound() {
        if (!this.enabled) return
        const ctx = this.getContext()
        const oscillator = ctx.createOscillator()
        const gainNode = ctx.createGain()

        oscillator.connect(gainNode)
        gainNode.connect(ctx.destination)

        oscillator.type = 'triangle'
        oscillator.frequency.setValueAtTime(400, ctx.currentTime)
        oscillator.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.15)

        gainNode.gain.setValueAtTime(0.08, ctx.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15)

        oscillator.start(ctx.currentTime)
        oscillator.stop(ctx.currentTime + 0.15)
    }

    // Translation reveal - soft chime
    playTranslateSound() {
        if (!this.enabled) return
        const ctx = this.getContext()

        // Play two tones for a chime effect
        const frequencies = [523, 659] // C5, E5

        frequencies.forEach((freq, i) => {
            const oscillator = ctx.createOscillator()
            const gainNode = ctx.createGain()

            oscillator.connect(gainNode)
            gainNode.connect(ctx.destination)

            oscillator.type = 'sine'
            oscillator.frequency.setValueAtTime(freq, ctx.currentTime)

            gainNode.gain.setValueAtTime(0.05, ctx.currentTime + i * 0.05)
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2 + i * 0.05)

            oscillator.start(ctx.currentTime + i * 0.05)
            oscillator.stop(ctx.currentTime + 0.2 + i * 0.05)
        })
    }

    // Completion fanfare - triumphant chord
    playCompleteSound() {
        if (!this.enabled) return
        const ctx = this.getContext()

        // Major chord: C, E, G, C (octave higher)
        const frequencies = [262, 330, 392, 523]

        frequencies.forEach((freq, i) => {
            const oscillator = ctx.createOscillator()
            const gainNode = ctx.createGain()

            oscillator.connect(gainNode)
            gainNode.connect(ctx.destination)

            oscillator.type = 'sine'
            oscillator.frequency.setValueAtTime(freq, ctx.currentTime)

            gainNode.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.1)
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8 + i * 0.1)

            oscillator.start(ctx.currentTime + i * 0.1)
            oscillator.stop(ctx.currentTime + 0.8 + i * 0.1)
        })
    }

    // Ambient scanning hum
    playScanningAmbient(): () => void {
        if (!this.enabled) return () => { }

        const ctx = this.getContext()
        const oscillator = ctx.createOscillator()
        const gainNode = ctx.createGain()
        const filter = ctx.createBiquadFilter()

        oscillator.connect(filter)
        filter.connect(gainNode)
        gainNode.connect(ctx.destination)

        oscillator.type = 'sawtooth'
        oscillator.frequency.setValueAtTime(80, ctx.currentTime)

        filter.type = 'lowpass'
        filter.frequency.setValueAtTime(200, ctx.currentTime)
        filter.Q.setValueAtTime(5, ctx.currentTime)

        gainNode.gain.setValueAtTime(0.03, ctx.currentTime)

        oscillator.start(ctx.currentTime)

        // Return stop function
        return () => {
            gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5)
            oscillator.stop(ctx.currentTime + 0.5)
        }
    }
}

// Singleton instance
export const soundEffects = new SoundGenerator()

// React hook for sound effects
export function useSoundEffects() {
    const [enabled, setEnabled] = useState(soundEffects.isEnabled())

    const toggleSound = () => {
        const newState = !enabled
        setEnabled(newState)
        soundEffects.setEnabled(newState)
    }

    return {
        enabled,
        toggleSound,
        playScanBeep: () => soundEffects.playScanBeep(),
        playDetectSound: () => soundEffects.playDetectSound(),
        playTranslateSound: () => soundEffects.playTranslateSound(),
        playCompleteSound: () => soundEffects.playCompleteSound(),
        playScanningAmbient: () => soundEffects.playScanningAmbient(),
    }
}
