import { useEffect, useRef } from 'react'

interface Particle {
    x: number
    y: number
    vx: number
    vy: number
    size: number
    opacity: number
    char: string
}

interface ParticleSystemProps {
    isActive: boolean
    intensity?: 'low' | 'medium' | 'high'
}

export function ParticleSystem({ isActive, intensity = 'medium' }: ParticleSystemProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const particlesRef = useRef<Particle[]>([])
    const animationRef = useRef<number>()

    const cuneiformChars = ['𒀀', '𒀭', '𒆠', '𒇻', '𒁺', '𒊕', '𒃲', '𒆳', '𒌓', '𒈬']

    const particleCount = {
        low: 15,
        medium: 30,
        high: 50
    }[intensity]

    useEffect(() => {
        if (!isActive || !canvasRef.current) return

        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        // Set canvas size
        const resizeCanvas = () => {
            canvas.width = canvas.offsetWidth
            canvas.height = canvas.offsetHeight
        }
        resizeCanvas()
        window.addEventListener('resize', resizeCanvas)

        // Initialize particles
        particlesRef.current = Array.from({ length: particleCount }, () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5 - 0.3, // Slight upward drift
            size: Math.random() * 12 + 8,
            opacity: Math.random() * 0.5 + 0.1,
            char: cuneiformChars[Math.floor(Math.random() * cuneiformChars.length)]
        }))

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height)

            particlesRef.current.forEach(particle => {
                // Update position
                particle.x += particle.vx
                particle.y += particle.vy

                // Wrap around edges
                if (particle.x < 0) particle.x = canvas.width
                if (particle.x > canvas.width) particle.x = 0
                if (particle.y < 0) particle.y = canvas.height
                if (particle.y > canvas.height) particle.y = 0

                // Slowly change opacity
                particle.opacity += (Math.random() - 0.5) * 0.02
                particle.opacity = Math.max(0.1, Math.min(0.6, particle.opacity))

                // Draw particle
                ctx.save()
                ctx.globalAlpha = particle.opacity
                ctx.fillStyle = '#00d4ff'
                ctx.font = `${particle.size}px serif`
                ctx.shadowColor = '#00d4ff'
                ctx.shadowBlur = 10
                ctx.fillText(particle.char, particle.x, particle.y)
                ctx.restore()
            })

            animationRef.current = requestAnimationFrame(animate)
        }

        animate()

        return () => {
            window.removeEventListener('resize', resizeCanvas)
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current)
            }
        }
    }, [isActive, particleCount])

    if (!isActive) return null

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-none z-10"
            style={{ opacity: 0.6 }}
        />
    )
}
