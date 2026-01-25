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
 * Global API availability tracking with aggressive failure handling
 * Allow ONE attempt, then block on any failure, but retry after 30s
 */
let globalApiCircuitOpen = false  // Start OPEN (allow calls)
let hasFailedOnce = false
let lastFailureTime = 0
const CIRCUIT_RESET_TIME_MS = 30000 // 30 seconds

export function isApiAvailable(): boolean {
    if (!IS_BACKEND_CONFIGURED) return false

    // If circuit is broken, check if enough time has passed to retry (probe)
    if (globalApiCircuitOpen) {
        const now = Date.now()
        if (now - lastFailureTime > CIRCUIT_RESET_TIME_MS) {
            // Allow one probe request
            return true
        }
        return false
    }

    return true
}

export function reportApiFailure(): void {
    const now = Date.now()
    // Update failure time but don't spam console
    lastFailureTime = now

    if (!hasFailedOnce) {
        hasFailedOnce = true
        globalApiCircuitOpen = true
        console.warn('[API] Backend connection failed - temporarily disabling API calls for 30s')
    } else if (!globalApiCircuitOpen) {
        // Circuit was closed (mostly working), but just failed again
        globalApiCircuitOpen = true
        console.warn('[API] Backend connection failed again - disabling API calls for 30s')
    }
}

export function reportApiSuccess(): void {
    if (hasFailedOnce || globalApiCircuitOpen) {
        console.log('[API] Backend connection restored')
        hasFailedOnce = false
        globalApiCircuitOpen = false
        lastFailureTime = 0
    }
}

// Only log in development
if (isDevelopment) {
    console.log('Environment Config:', {
        API_BASE_URL: API_BASE_URL || '(not configured)',
        SOCKET_URL: SOCKET_URL || '(not configured)',
        IS_BACKEND_CONFIGURED
    })
}
