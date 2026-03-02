/**
 * Auth API module.
 */
import apiClient, { setToken, clearToken } from './client'
import type { LoginRequest, TokenResponse } from '@/types'

export async function login(data: LoginRequest): Promise<TokenResponse> {
    const res = await apiClient.post<TokenResponse>('/auth/login', data)
    setToken(res.data.access_token)
    return res.data
}

export function logout(): void {
    clearToken()
}
