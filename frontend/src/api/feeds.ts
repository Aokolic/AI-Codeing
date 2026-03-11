/**
 * Data feeds API module (T029).
 */
import apiClient from './client'
import type {
    CollectTriggerResponse,
    DataFeedCreate,
    DataFeedOut,
    DataFeedUpdate,
    PaginatedResponse,
} from '@/types'

export async function listFeeds(
    page = 1,
    page_size = 20,
): Promise<PaginatedResponse<DataFeedOut>> {
    const res = await apiClient.get<PaginatedResponse<DataFeedOut>>('/feeds', {
        params: { page, page_size },
    })
    return res.data
}

export async function createFeed(data: DataFeedCreate): Promise<DataFeedOut> {
    const res = await apiClient.post<DataFeedOut>('/feeds', data)
    return res.data
}

export async function updateFeed(id: string, data: DataFeedUpdate): Promise<DataFeedOut> {
    const res = await apiClient.patch<DataFeedOut>(`/feeds/${id}`, data)
    return res.data
}

export async function deleteFeed(id: string): Promise<void> {
    await apiClient.delete(`/feeds/${id}`)
}

export async function triggerCollect(feedId: string): Promise<CollectTriggerResponse> {
    const res = await apiClient.post<CollectTriggerResponse>(`/feeds/${feedId}/collect`, null, {
        timeout: 120_000,
    })
    return res.data
}
