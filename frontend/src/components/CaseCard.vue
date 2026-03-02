<template>
    <router-link :to="`/cases/${caseData.id}`" class="case-card-link">
        <article class="case-card" :class="`status-${caseData.status}`">
            <!-- Status accent bar -->
            <div class="status-bar"></div>

            <div class="card-body">
                <!-- Title row -->
                <div class="case-header">
                    <span class="case-title">{{ caseData.title }}</span>
                    <span class="status-badge" :class="`sbadge-${caseData.status}`">
                        {{ statusLabel[caseData.status] ?? caseData.status }}
                    </span>
                </div>

                <!-- Stats row -->
                <div class="case-stats">
                    <span class="stat">
                        <span class="stat-icon">🔥</span>
                        <span class="stat-val flame-val">{{ Math.round(caseData.hotness_score) }}</span>
                    </span>
                    <span class="stat-sep">·</span>
                    <span class="stat">{{ caseData.event_count }} 事件</span>
                    <span class="stat-sep">·</span>
                    <span class="stat">{{ caseData.source_count }} 来源</span>
                    <template v-if="caseData.last_event_at">
                        <span class="stat-sep">·</span>
                        <span class="stat last-event">{{ fromNow(caseData.last_event_at) }}</span>
                    </template>
                </div>

                <!-- Tags -->
                <div v-if="caseData.tags?.length" class="case-tags">
                    <span v-for="tag in caseData.tags" :key="tag.id" class="tag-chip">
                        {{ tag.name }}
                    </span>
                </div>
            </div>
        </article>
    </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import type { CaseSummary } from '@/types'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const props = defineProps<{ case: CaseSummary }>()
const caseData = computed(() => props.case)

const statusLabel: Record<string, string> = {
    active: '进行中',
    resolved: '已解决',
    archived: '已归档',
    observing: '待观察',
    closed: '已结案',
}

function fromNow(dateStr: string) {
    return dayjs(dateStr).fromNow()
}
</script>

<style scoped>
.case-card-link {
    text-decoration: none;
    display: block;
}

/* Card container */
.case-card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(15, 23, 42, .07), 0 1px 2px rgba(15, 23, 42, .04);
    display: flex;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
    cursor: pointer;
}

.case-card:hover {
    box-shadow: 0 6px 20px rgba(79, 70, 229, .12), 0 2px 6px rgba(15, 23, 42, .06);
    transform: translateY(-2px);
}

/* Accent bar on left */
.status-bar {
    width: 4px;
    flex-shrink: 0;
    background: #e2e8f0;
    border-radius: 0;
}

.status-active .status-bar {
    background: linear-gradient(180deg, #f59e0b, #ef4444);
}

.status-resolved .status-bar {
    background: linear-gradient(180deg, #10b981, #059669);
}

.status-closed .status-bar {
    background: linear-gradient(180deg, #6366f1, #4f46e5);
}

.status-observing .status-bar {
    background: linear-gradient(180deg, #3b82f6, #1d4ed8);
}

.status-archived .status-bar {
    background: #94a3b8;
}

.card-body {
    flex: 1;
    padding: 14px 16px;
    min-width: 0;
}

/* Header row */
.case-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 8px;
}

.case-title {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
    flex: 1;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* Status badge */
.status-badge {
    flex-shrink: 0;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 999px;
    letter-spacing: 0.02em;
}

.sbadge-active {
    background: #fef3c7;
    color: #d97706;
}

.sbadge-resolved {
    background: #d1fae5;
    color: #059669;
}

.sbadge-closed {
    background: #ede9fe;
    color: #4f46e5;
}

.sbadge-observing {
    background: #dbeafe;
    color: #2563eb;
}

.sbadge-archived {
    background: #f1f5f9;
    color: #64748b;
}

/* Stats row */
.case-stats {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
    font-size: 12px;
    color: #64748b;
    margin-bottom: 8px;
}

.stat {
    display: flex;
    align-items: center;
    gap: 2px;
}

.stat-icon {
    font-size: 12px;
}

.flame-val {
    font-weight: 700;
    color: #f97316;
}

.stat-sep {
    color: #cbd5e1;
    margin: 0 2px;
}

.last-event {
    color: #94a3b8;
    font-style: italic;
}

/* Tags */
.case-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.tag-chip {
    font-size: 11px;
    padding: 1px 7px;
    background: #f0f4ff;
    color: #4f46e5;
    border-radius: 999px;
    border: 1px solid #e0e7ff;
    font-weight: 500;
}
</style>
