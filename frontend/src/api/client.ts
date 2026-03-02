/**
 * HTTP API client — axios with JWT header injection and error interceptors.
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'

// @ts-ignore — Vite injects import.meta.env at build time
const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL ?? '/api/v1'

const apiClient: AxiosInstance = axios.create({
    baseURL: BASE_URL,
    timeout: 15_000,
    headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: inject JWT Bearer token if available ────────────────
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// ── Response interceptor: normalise errors ───────────────────────────────────
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError<{ detail?: string }>) => {
        const message =
            error.response?.data?.detail ??
            error.message ??
            '请求失败，请稍后重试'
        return Promise.reject(new Error(message))
    },
)

export default apiClient

// ─── Auth helpers ─────────────────────────────────────────────────────────────

export function setToken(token: string): void {
    localStorage.setItem('access_token', token)
}

export function clearToken(): void {
    localStorage.removeItem('access_token')
}

export function hasToken(): boolean {
    return !!localStorage.getItem('access_token')
}
