<template>
    <div class="timeline-wrapper">
        <div class="timeline-header">
            <span class="tl-title">📅 事件时间线</span>
            <span v-if="events.length" class="tl-count">{{ events.length }} 个节点</span>
        </div>

        <div v-if="loading" class="timeline-loading">
            <n-spin size="large" />
        </div>

        <n-empty v-else-if="!events.length" description="暂无时间轴事件" class="timeline-empty" />

        <template v-else>
            <n-timeline class="custom-timeline">
                <n-timeline-item v-for="event in events" :key="event.id" :time="formatTime(event.event_time)"
                    :type="timelineItemType(event)">
                    <event-card :event="event" @expand="emit('event-click', $event)" />
                </n-timeline-item>
            </n-timeline>
        </template>
    </div>
</template>

<script setup lang="ts">
import { NTimeline, NTimelineItem, NSpin, NEmpty } from 'naive-ui'
import EventCard from './EventCard.vue'
import dayjs from 'dayjs'
import type { EventSummary, CredibilityLevel } from '@/types'

defineProps<{
    events: EventSummary[]
    loading: boolean
}>()

const emit = defineEmits<{
    (e: 'event-click', id: string): void
}>()

function formatTime(t: string) {
    return dayjs(t).format('YYYY-MM-DD')
}

function timelineItemType(event: EventSummary): 'success' | 'info' | 'warning' | 'error' | 'default' {
    const levelMap: Record<CredibilityLevel, 'success' | 'info' | 'warning' | 'error'> = {
        high: 'success',
        medium: 'info',
        low: 'warning',
        unverified: 'error',
    }
    return event.credibility ? levelMap[event.credibility.level] : 'default'
}
</script>

<style scoped>
.timeline-wrapper {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 6px rgba(15, 23, 42, .06);
    overflow: hidden;
}

.timeline-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px 12px;
    border-bottom: 1px solid #f1f5f9;
}

.tl-title {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
}

.tl-count {
    font-size: 12px;
    padding: 2px 10px;
    background: #e0e7ff;
    color: #4f46e5;
    border-radius: 999px;
    font-weight: 600;
}

.timeline-loading,
.timeline-empty {
    display: flex;
    justify-content: center;
    padding: 48px 0;
}

.custom-timeline {
    padding: 16px 20px;
}
</style>
