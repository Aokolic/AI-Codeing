<template>
    <div class="event-card" :class="credibilityClass" data-testid="event-card" @click="handleClick">
        <!-- Timeline dot -->
        <div class="timeline-dot"></div>

        <div class="event-body">
            <div class="event-header">
                <div class="event-meta">
                    <span class="event-time">🕐 {{ formatTime(event.event_time) }}</span>
                    <span class="meta-sep">·</span>
                    <span class="source-count">{{ event.source_count }} 来源</span>
                </div>
                <credibility-badge v-if="event.credibility" :level="event.credibility.level"
                    :score="event.credibility.total_score" />
            </div>

            <div class="event-title">{{ event.title }}</div>

            <!-- T059: low-credibility / conflict warning -->
            <div v-if="showWarning" class="credibility-warning">
                <span class="warn-icon">⚠️</span>
                <span v-if="event.credibility?.has_conflict">来源存在分歧，请交叉核实</span>
                <span v-else>可信度较低（{{ event.credibility?.level }}），尚未充分核实</span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CredibilityBadge from './CredibilityBadge.vue'
import dayjs from 'dayjs'
import type { EventSummary } from '@/types'

const props = defineProps<{ event: EventSummary }>()
const emit = defineEmits<{ (e: 'expand', id: string): void }>()

function handleClick() {
    emit('expand', props.event.id)
}

function formatTime(t: string) {
    return dayjs(t).format('YYYY-MM-DD HH:mm')
}

const credibilityClass = computed(() => {
    const level = props.event.credibility?.level
    return { [`credibility-${level}`]: !!level }
})

const showWarning = computed(() => {
    const c = props.event.credibility
    if (!c) return false
    return c.has_conflict || c.level === 'low' || c.level === 'unverified'
})
</script>

<style scoped>
.event-card {
    display: flex;
    gap: 0;
    padding: 14px 16px 14px 0;
    border-radius: 0;
    cursor: pointer;
    transition: background 0.15s;
    position: relative;
}

.event-card:hover {
    background: rgba(79, 70, 229, .03);
    border-radius: 8px;
}

/* Colored left accent per credibility level */
.credibility-low .timeline-dot {
    background: #d97706;
    box-shadow: 0 0 0 4px #fef3c7;
}

.credibility-unverified .timeline-dot {
    background: #dc2626;
    box-shadow: 0 0 0 4px #fee2e2;
}

.credibility-medium .timeline-dot {
    background: #2563eb;
    box-shadow: 0 0 0 4px #dbeafe;
}

.credibility-high .timeline-dot {
    background: #059669;
    box-shadow: 0 0 0 4px #d1fae5;
}

/* Timeline dot */
.timeline-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #cbd5e1;
    flex-shrink: 0;
    margin-top: 5px;
    margin-right: 14px;
    margin-left: 4px;
    transition: all 0.15s;
}

.event-body {
    flex: 1;
    min-width: 0;
}

.event-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    gap: 8px;
}

.event-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #64748b;
}

.meta-sep {
    color: #cbd5e1;
}

.event-time {
    font-variant-numeric: tabular-nums;
}

.source-count {
    color: #94a3b8;
}

.event-title {
    font-size: 14px;
    font-weight: 500;
    color: #0f172a;
    line-height: 1.5;
}

/* Warning strip */
.credibility-warning {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    padding: 5px 10px;
    background: #fffbeb;
    border: 1px solid #fef08a;
    border-radius: 6px;
    font-size: 12px;
    color: #92400e;
}

.credibility-low .credibility-warning,
.credibility-unverified .credibility-warning {
    background: #fff1f2;
    border-color: #fecdd3;
    color: #9f1239;
}

.warn-icon {
    flex-shrink: 0;
    font-size: 13px;
}
</style>
