<template>
    <div class="timeline-wrapper">
        <div v-if="loading" class="timeline-loading">
            <n-spin size="large" />
        </div>

        <n-empty v-else-if="!events.length" description="暂无时间轴事件" class="timeline-empty" />

        <div v-else class="event-list">
            <event-card v-for="event in events" :key="event.id" :event="event" @expand="emit('event-click', $event)" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { NSpin, NEmpty } from 'naive-ui'
import EventCard from './EventCard.vue'
import type { EventSummary } from '@/types'

defineProps<{
    events: EventSummary[]
    loading: boolean
}>()

const emit = defineEmits<{
    (e: 'event-click', id: string): void
}>()
</script>

<style scoped>
.timeline-wrapper {
    min-height: 100px;
}

.event-list {
    padding: 8px 0;
}

.timeline-loading,
.timeline-empty {
    display: flex;
    justify-content: center;
    padding: 48px 0;
}
</style>
