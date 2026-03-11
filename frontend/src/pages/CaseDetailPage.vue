<template>
    <div class="case-detail-page">
        <!-- Loading skeleton -->
        <template v-if="loading">
            <n-skeleton text :repeat="3" />
        </template>

        <!-- Error state -->
        <n-result v-else-if="error" status="error" title="加载失败" :description="error">
            <template #footer>
                <n-button @click="load">重试</n-button>
            </template>
        </n-result>

        <!-- Case detail -->
        <template v-else-if="caseDetail">
            <!-- Breadcrumb -->
            <div class="breadcrumb">
                <router-link to="/" class="bc-link">热点</router-link>
                <span class="bc-sep">›</span>
                <span class="bc-current">跟踪</span>
            </div>

            <!-- Case header section -->
            <div class="detail-header">
                <h1 class="detail-title">{{ caseDetail.title }}</h1>
                <div class="detail-author">
                    <span class="author-name">系统采集</span>
                    <span class="author-sep">·</span>
                    <span class="author-time">{{ fromNow(caseDetail.created_at) }}</span>
                </div>
                <p v-if="caseDetail.description" class="detail-desc">{{ caseDetail.description }}</p>
            </div>

            <!-- Main content with sidebar -->
            <div class="detail-layout">
                <!-- Timeline main column -->
                <div class="detail-main">
                    <!-- Timeline -->
                    <timeline :events="timelineState.events.value" :loading="timelineState.loading.value"
                        @event-click="handleEventClick" />
                </div>

                <!-- Calendar sidebar -->
                <aside v-if="monthGroups.length" class="detail-sidebar">
                    <div v-for="mg in monthGroups" :key="mg.label" class="month-group">
                        <div class="month-label">{{ mg.label }}</div>
                        <div class="day-list">
                            <button v-for="d in mg.days" :key="d" class="day-btn"
                                :class="{ active: activeDay === `${mg.label}-${d}` }" @click="scrollToDay(mg.label, d)">
                                {{ d }}日
                            </button>
                        </div>
                    </div>
                </aside>
            </div>
        </template>

        <!-- Credibility drawer -->
        <n-drawer v-model:show="drawerVisible" :width="480" title="可信度详情">
            <n-drawer-content>
                <div v-if="credLoading" class="drawer-loading"><n-spin /></div>
                <credibility-panel v-else-if="credDetail" :detail="credDetail" />
            </n-drawer-content>
        </n-drawer>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
    NSkeleton, NResult, NButton, NDrawer, NDrawerContent, NSpin,
} from 'naive-ui'
import Timeline from '@/components/Timeline.vue'
import CredibilityPanel from '@/components/CredibilityPanel.vue'
import { getCaseDetail } from '@/api/cases'
import { getCredibilityDetail } from '@/api/credibility'
import { useTimeline } from '@/composables/useTimeline'
import type { CaseDetail, CredibilityDetail } from '@/types'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const route = useRoute()
const caseId = computed(() => route.params.id as string)

const caseDetail = ref<CaseDetail | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const activeDay = ref('')

const timelineState = useTimeline(caseId.value)

const drawerVisible = ref(false)
const credDetail = ref<CredibilityDetail | null>(null)
const credLoading = ref(false)

function fromNow(dateStr: string) {
    return dayjs(dateStr).fromNow()
}

// Build month/day groups from events for sidebar calendar
const monthGroups = computed(() => {
    const events = timelineState.events.value
    if (!events.length) return []

    const groups: Map<string, Set<number>> = new Map()
    for (const e of events) {
        const d = dayjs(e.event_time)
        const label = `${d.month() + 1}月`
        if (!groups.has(label)) groups.set(label, new Set())
        groups.get(label)!.add(d.date())
    }

    return Array.from(groups.entries()).map(([label, days]) => ({
        label,
        days: Array.from(days).sort((a, b) => b - a),
    }))
})

function scrollToDay(month: string, day: number) {
    activeDay.value = `${month}-${day}`
    // Could scroll to specific event, for now just visual highlight
}

async function load() {
    loading.value = true
    error.value = null
    try {
        caseDetail.value = await getCaseDetail(caseId.value)
        await timelineState.fetchTimeline()
    } catch (e: unknown) {
        error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
        loading.value = false
    }
}

async function handleEventClick(eventId: string) {
    drawerVisible.value = true
    credLoading.value = true
    credDetail.value = null
    try {
        const result = await getCredibilityDetail(eventId)
        if (result.detail) credDetail.value = result.detail
    } catch {
        // silent
    } finally {
        credLoading.value = false
    }
}

onMounted(load)
</script>

<style scoped>
.case-detail-page {
    max-width: 960px;
    margin: 0 auto;
}

/* Breadcrumb */
.breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
    font-size: 14px;
}

.bc-link {
    color: #ef4444;
    text-decoration: none;
    font-weight: 500;
}

.bc-link:hover {
    text-decoration: underline;
}

.bc-sep {
    color: #d1d5db;
}

.bc-current {
    color: #9ca3af;
}

/* Header */
.detail-header {
    margin-bottom: 28px;
    padding-bottom: 24px;
    border-bottom: 1px solid #f3f4f6;
}

.detail-title {
    font-size: 28px;
    font-weight: 800;
    color: #1a1a1a;
    margin: 0 0 12px;
    line-height: 1.35;
    letter-spacing: -0.02em;
}

.detail-author {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #9ca3af;
    margin-bottom: 16px;
}

.author-name {
    color: #6b7280;
}

.author-sep {
    color: #d1d5db;
}

.detail-desc {
    font-size: 15px;
    color: #4b5563;
    line-height: 1.8;
    margin: 0;
}

/* Layout */
.detail-layout {
    display: flex;
    gap: 32px;
}

.detail-main {
    flex: 1;
    min-width: 0;
}

/* Sidebar calendar */
.detail-sidebar {
    width: 100px;
    flex-shrink: 0;
    padding-top: 48px;
}

.month-group {
    margin-bottom: 16px;
}

.month-label {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
}

.day-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
}

.day-btn {
    background: none;
    border: none;
    padding: 4px 8px;
    font-size: 14px;
    color: #6b7280;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.15s;
    width: 100%;
    text-align: left;
}

.day-btn:hover {
    background: #f3f4f6;
    color: #1a1a1a;
}

.day-btn.active {
    color: #ef4444;
    font-weight: 600;
    background: #fef2f2;
}

/* Drawer */
.drawer-loading {
    display: flex;
    justify-content: center;
    padding: 60px 0;
}

@media (max-width: 768px) {
    .detail-sidebar {
        display: none;
    }

    .detail-title {
        font-size: 22px;
    }
}
</style>
