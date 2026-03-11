<template>
    <div class="event-card" data-testid="event-card" @click="handleClick">
        <!-- Timeline dot -->
        <div class="timeline-dot-wrap">
            <div class="timeline-dot" :class="dotColor"></div>
            <div class="timeline-line"></div>
        </div>

        <div class="event-body">
            <!-- Date badge -->
            <div class="event-date-row">
                <span class="date-badge" :class="dotColor">● {{ formatDate(event.event_time) }}</span>
                <span class="date-relative">{{ fromNow(event.event_time) }}</span>
            </div>

            <!-- Title -->
            <h3 class="event-title">{{ event.title }}</h3>

            <!-- Source info -->
            <div class="event-source-row">
                <span class="source-name">采集来源</span>
                <span class="source-time">{{ formatTime(event.event_time) }}</span>
                <span class="source-count">{{ event.source_count }} 来源</span>
                <credibility-badge v-if="event.credibility" :level="event.credibility.level"
                    :score="event.credibility.total_score" />
                <!-- Source icons -->
                <div v-if="event.sources && event.sources.length > 0" class="source-icons">
                    <div v-for="(src, i) in displaySources" :key="src.id" class="source-icon"
                        :style="{ backgroundColor: sourceColor(src.source_type), zIndex: displaySources.length - i }"
                        :title="`${src.name || '?'} — ${src.source_type}`">
                        {{ src.name ? src.name.charAt(0) : '?' }}
                    </div>
                    <div v-if="overflowCount > 0" class="source-icon overflow" :title="`还有 ${overflowCount} 个来源`">
                        +{{ overflowCount }}
                    </div>
                </div>
            </div>

            <!-- Warning -->
            <div v-if="showWarning" class="credibility-warning">
                ⚠️
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
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import type { EventSummary, SourceType } from '@/types'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const SOURCE_TYPE_COLORS: Record<SourceType, string> = {
    government: '#ef4444',
    mainstream_media: '#3b82f6',
    academic: '#8b5cf6',
    local_media: '#06b6d4',
    social_media: '#f97316',
    unknown: '#9ca3af',
}

const MAX_VISIBLE_SOURCES = 3

const props = defineProps<{ event: EventSummary }>()
const emit = defineEmits<{ (e: 'expand', id: string): void }>()

const displaySources = computed(() => (props.event.sources ?? []).slice(0, MAX_VISIBLE_SOURCES))
const overflowCount = computed(() => Math.max(0, (props.event.sources?.length ?? 0) - MAX_VISIBLE_SOURCES))

function sourceColor(type: string): string {
    return SOURCE_TYPE_COLORS[type as SourceType] ?? SOURCE_TYPE_COLORS.unknown
}

function handleClick() {
    emit('expand', props.event.id)
}

function formatDate(t: string) {
    return dayjs(t).format('MM/DD')
}

function formatTime(t: string) {
    return dayjs(t).format('HH:mm')
}

function fromNow(t: string) {
    return dayjs(t).fromNow()
}

const dotColor = computed(() => {
    const level = props.event.credibility?.level
    if (!level) return 'dot-default'
    return `dot-${level}`
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
    padding: 0 0 24px;
    cursor: pointer;
    position: relative;
}

.event-card:hover .event-title {
    color: #ef4444;
}

/* Timeline dot */
.timeline-dot-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 24px;
    flex-shrink: 0;
    padding-top: 4px;
}

.timeline-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #d1d5db;
    flex-shrink: 0;
    z-index: 1;
}

.timeline-line {
    width: 2px;
    flex: 1;
    background: #e5e7eb;
    margin-top: 4px;
}

.event-card:last-child .timeline-line {
    display: none;
}

.dot-default {
    background: #d1d5db;
}

.dot-high {
    background: #059669;
}

.dot-medium {
    background: #7c3aed;
}

.dot-low {
    background: #f59e0b;
}

.dot-unverified {
    background: #ef4444;
}

.event-body {
    flex: 1;
    min-width: 0;
    padding-left: 12px;
}

/* Date row */
.event-date-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.date-badge {
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    padding: 2px 8px;
    border-radius: 4px;
    background: #ef4444;
}

.date-badge.dot-high {
    background: #059669;
    color: #fff;
}

.date-badge.dot-medium {
    background: #7c3aed;
    color: #fff;
}

.date-badge.dot-low {
    background: #f59e0b;
    color: #fff;
}

.date-badge.dot-unverified {
    background: #ef4444;
    color: #fff;
}

.date-badge.dot-default {
    background: #ef4444;
    color: #fff;
}

.date-relative {
    font-size: 13px;
    color: #9ca3af;
}

/* Title */
.event-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 8px;
    line-height: 1.5;
    transition: color 0.15s;
}

/* Source row */
.event-source-row {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    color: #9ca3af;
    flex-wrap: wrap;
}

.source-name {
    color: #ef4444;
    font-weight: 500;
}

.source-count {
    color: #6b7280;
}

/* Source icons */
.source-icons {
    display: flex;
    align-items: center;
    margin-left: auto;
}

.source-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    border: 2px solid #fff;
    cursor: default;
    flex-shrink: 0;
}

.source-icon+.source-icon {
    margin-left: -8px;
}

.source-icon.overflow {
    background: #9ca3af;
    font-size: 11px;
}

/* Warning */
.credibility-warning {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    padding: 6px 12px;
    background: #fffbeb;
    border: 1px solid #fef08a;
    border-radius: 6px;
    font-size: 12px;
    color: #92400e;
}
</style>
