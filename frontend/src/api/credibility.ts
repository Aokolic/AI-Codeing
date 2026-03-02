/**
 * Credibility API module (T055).
 */
import apiClient from './client'
import type { CredibilityOverall } from '@/types'

export async function getCredibilityDetail(eventId: string): Promise<CredibilityOverall> {
    const res = await apiClient.get<CredibilityOverall>(`/events/${eventId}/credibility`)
    return res.data
}
