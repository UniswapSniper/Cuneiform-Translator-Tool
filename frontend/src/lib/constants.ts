/**
 * Smart URL detection for API and WebSocket endpoints.
 * 
 * In production (HTTPS), we require explicit environment variables.
 * Falling back to localhost on HTTPS causes mixed content blocking
 * and infinite reconnection loops that crash the browser.
 */

const isSecureContext = typeof window !== 'undefined' && window.location?.protocol === 'https:'
const isDevelopment = import.meta.env.DEV

// Get configured URLs from environment
const configuredApiUrl = import.meta.env.VITE_API_URL
const configuredSocketUrl = import.meta.env.VITE_SOCKET_URL

// In development, fall back to localhost. In production (HTTPS), require explicit config.
export const API_BASE_URL: string | null = configuredApiUrl
    ? configuredApiUrl
    : (isDevelopment && !isSecureContext)
        ? 'http://localhost:5001/api'
        : null

export const SOCKET_URL: string | null = configuredSocketUrl
    ? configuredSocketUrl
    : (isDevelopment && !isSecureContext)
        ? 'http://localhost:5001'
        : null

// Flag to indicate if backend is configured
export const IS_BACKEND_CONFIGURED = API_BASE_URL !== null && SOCKET_URL !== null

/**
 * Global API availability tracking - prevents cascading failures across components
 */
let globalApiFailureCount = 0
let globalApiCircuitOpen = false
const GLOBAL_MAX_FAILURES = 2  // Very aggressive - 2 failures and we stop

export function isApiAvailable(): boolean {
    return !globalApiCircuitOpen && IS_BACKEND_CONFIGURED
}

export function reportApiFailure(): void {
    globalApiFailureCount++
    if (globalApiFailureCount >= GLOBAL_MAX_FAILURES && !globalApiCircuitOpen) {
        globalApiCircuitOpen = true
        console.warn(`[API] Global circuit breaker opened after ${GLOBAL_MAX_FAILURES} failures. All API calls disabled.`)
    }
}

export function reportApiSuccess(): void {
    globalApiFailureCount = 0
    // Don't auto-reset circuit - require page reload
}

// Only log in development, and only once
if (isDevelopment) {
    console.log('Environment Config:', {
        API_BASE_URL: API_BASE_URL || '(not configured)',
        SOCKET_URL: SOCKET_URL || '(not configured)',
        IS_BACKEND_CONFIGURED
    })
}
