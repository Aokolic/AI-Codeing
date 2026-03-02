/**
 * Events API module — timeline + event detail (T043).
 */
import apiClient from './client'
import type { EventDetail, EventSummary } from '@/types'

export async function getTimeline(
    caseId: string,
    params?: { from?: string; to?: string },
): Promise<EventSummary[]> {
    const res = await apiClient.get<EventSummary[]>(`/cases/${caseId}/events`, { params })
    return res.data
}

export async function getEventDetail(eventId: string): Promise<EventDetail> {
    const res = await apiClient.get<EventDetail>(`/events/${eventId}`)
    return res.data
}
