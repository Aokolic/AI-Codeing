/**
 * Cases API module — list, get, create, update, search (T042, T066).
 */
import apiClient from './client'
import type {
    CaseCreate,
    CaseDetail,
    CaseSummary,
    CaseUpdate,
    PaginatedResponse,
    TagOut,
    TagWithCount,
} from '@/types'

export async function listCases(params?: {
    page?: number
    page_size?: number
    status?: string
    tag_id?: string
    sort?: 'hotness' | 'created_at'
}): Promise<PaginatedResponse<CaseSummary>> {
    const res = await apiClient.get<PaginatedResponse<CaseSummary>>('/cases', { params })
    return res.data
}

export async function getCaseDetail(id: string): Promise<CaseDetail> {
    const res = await apiClient.get<CaseDetail>(`/cases/${id}`)
    return res.data
}

export async function createCase(data: CaseCreate): Promise<CaseDetail> {
    const res = await apiClient.post<CaseDetail>('/cases', data)
    return res.data
}

export async function updateCase(id: string, data: CaseUpdate): Promise<CaseDetail> {
    const res = await apiClient.patch<CaseDetail>(`/cases/${id}`, data)
    return res.data
}

export async function searchCases(
    q: string,
    limit = 10,
): Promise<CaseSummary[]> {
    const res = await apiClient.get<CaseSummary[]>('/cases/search', {
        params: { q, limit },
    })
    return res.data
}

export async function listTags(): Promise<TagWithCount[]> {
    const res = await apiClient.get<TagWithCount[]>('/tags')
    return res.data
}

export async function createTag(name: string): Promise<TagOut> {
    const res = await apiClient.post<TagOut>('/tags', { id: '', name })
    return res.data
}
