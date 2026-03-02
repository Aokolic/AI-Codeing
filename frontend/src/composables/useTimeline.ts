import { ref, computed } from 'vue'
import { getTimeline } from '@/api/events'
import type { EventSummary } from '@/types'

export interface TimelineFilters {
    from?: string
    to?: string
}

export function useTimeline(caseId: string) {
    const events = ref<EventSummary[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)
    const filters = ref<TimelineFilters>({})

    const filteredEvents = computed(() => {
        return events.value.filter((e) => {
            const t = new Date(e.event_time).getTime()
            if (filters.value.from && t < new Date(filters.value.from).getTime()) return false
            if (filters.value.to && t > new Date(filters.value.to).getTime()) return false
            return true
        })
    })

    async function fetchTimeline() {
        loading.value = true
        error.value = null
        try {
            const params: Record<string, string | undefined> = {}
            if (filters.value.from) params.from_time = filters.value.from
            if (filters.value.to) params.to_time = filters.value.to
            events.value = await getTimeline(caseId, params)
        } catch (e: unknown) {
            error.value = e instanceof Error ? e.message : '加载失败'
        } finally {
            loading.value = false
        }
    }

    function applyFilter(newFilters: TimelineFilters) {
        filters.value = { ...newFilters }
    }

    function clearFilter() {
        filters.value = {}
    }

    return { events: filteredEvents, allEvents: events, loading, error, filters, fetchTimeline, applyFilter, clearFilter }
}
