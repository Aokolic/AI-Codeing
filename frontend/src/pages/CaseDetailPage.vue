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
            <!-- Header -->
            <div class="case-header">
                <div class="header-top">
                    <n-breadcrumb>
                        <n-breadcrumb-item href="/">首页</n-breadcrumb-item>
                        <n-breadcrumb-item>{{ caseDetail.title }}</n-breadcrumb-item>
                    </n-breadcrumb>
                </div>
                <div class="header-main">
                    <h1 class="case-title">{{ caseDetail.title }}</h1>
                    <n-tag :type="statusTagType" size="medium" style="margin-left: 12px;">{{ statusLabel }}</n-tag>
                </div>
                <p v-if="caseDetail.description" class="case-desc">{{ caseDetail.description }}</p>
                <div class="case-stats">
                    <n-statistic label="热度" :value="Math.round(caseDetail.hotness_score)" />
                    <n-statistic label="事件数" :value="caseDetail.event_count" />
                    <n-statistic label="来源数" :value="caseDetail.source_count" />
                </div>
                <div v-if="caseDetail.tags?.length" class="case-tags">
                    <n-tag v-for="tag in caseDetail.tags" :key="tag.id" size="small" style="margin-right: 6px;">
                        {{ tag.name }}
                    </n-tag>
                </div>
            </div>

            <!-- Time filter -->
            <div class="filter-bar">
                <n-date-picker v-model:value="dateRange" type="daterange" clearable placeholder="开始时间 - 结束时间"
                    @update:value="handleDateFilter" />
            </div>

            <!-- Timeline -->
            <timeline :events="timelineState.events.value" :loading="timelineState.loading.value"
                @event-click="handleEventClick" />
        </template>

        <!-- Credibility drawer (T058) -->
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
    NSkeleton, NResult, NButton, NTag, NBreadcrumb, NBreadcrumbItem,
    NStatistic, NDatePicker, NDrawer, NDrawerContent, NSpin,
} from 'naive-ui'
import Timeline from '@/components/Timeline.vue'
import CredibilityPanel from '@/components/CredibilityPanel.vue'
import { getCaseDetail } from '@/api/cases'
import { getCredibilityDetail } from '@/api/credibility'
import { useTimeline } from '@/composables/useTimeline'
import type { CaseDetail, CredibilityDetail } from '@/types'

const route = useRoute()
const caseId = computed(() => route.params.id as string)

const caseDetail = ref<CaseDetail | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const timelineState = useTimeline(caseId.value)

const dateRange = ref<[number, number] | null>(null)

const drawerVisible = ref(false)
const credDetail = ref<CredibilityDetail | null>(null)
const credLoading = ref(false)

const statusLabelMap: Record<string, string> = {
    active: '进行中', resolved: '已解决', archived: '已归档', observing: '待观察', closed: '已结案',
}
const statusLabel = computed(() => caseDetail.value ? statusLabelMap[caseDetail.value.status] : '')
const statusTagType = computed(() => {
    const map: Record<string, 'success' | 'warning' | 'default'> = {
        active: 'warning', resolved: 'success', archived: 'default', observing: 'default', closed: 'success',
    }
    return caseDetail.value ? (map[caseDetail.value.status] ?? 'default') : 'default'
})

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

function handleDateFilter(val: [number, number] | null) {
    if (!val) {
        timelineState.clearFilter()
    } else {
        timelineState.applyFilter({
            from: new Date(val[0]).toISOString(),
            to: new Date(val[1]).toISOString(),
        })
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
    max-width: 900px;
    margin: 0 auto;
}

/* Header card */
.case-header {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: 0 1px 6px rgba(15, 23, 42, .06);
}

.header-top {
    margin-bottom: 12px;
}

.header-main {
    display: flex;
    align-items: flex-start;
    margin-bottom: 12px;
    gap: 12px;
}

.case-title {
    font-size: 22px;
    font-weight: 700;
    margin: 0;
    color: #0f172a;
    line-height: 1.35;
}

.case-desc {
    color: #64748b;
    font-size: 14px;
    margin: 0 0 16px;
    line-height: 1.6;
}

.case-stats {
    display: flex;
    gap: 28px;
    margin-bottom: 14px;
    padding: 14px 16px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.case-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

/* Filter bar */
.filter-bar {
    margin-bottom: 16px;
}

/* Drawer */
.drawer-loading {
    display: flex;
    justify-content: center;
    padding: 60px 0;
}
</style>
