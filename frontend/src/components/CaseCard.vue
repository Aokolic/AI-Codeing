<template>
    <router-link :to="`/cases/${caseData.id}`" class="case-card-link">
        <article class="case-card">
            <h3 class="case-title">{{ caseData.title }}</h3>

            <!-- Description preview (use title repeat if no description available) -->
            <p v-if="caseData.tags?.length || caseData.source_count" class="case-desc">
                {{ descText }}
            </p>

            <!-- Meta row -->
            <div class="case-meta">
                <div class="meta-left">
                    <span class="meta-hotness">
                        <span class="hotness-icon">↗</span>
                        {{ Math.round(caseData.hotness_score) }}
                    </span>
                    <span class="meta-sep">·</span>
                    <span class="meta-time">{{ fromNow(caseData.created_at) }}</span>
                    <template v-if="caseData.last_event_at">
                        <span class="meta-sep">·</span>
                        <span class="meta-tracking">【追踪】最新动态：{{ fromNow(caseData.last_event_at) }}</span>
                    </template>
                </div>
                <div class="meta-right">
                    <span class="event-badge">{{ caseData.event_count }} 事件</span>
                    <span class="source-badge">{{ caseData.source_count }} 来源</span>
                </div>
            </div>

            <!-- Tags row -->
            <div v-if="caseData.tags?.length" class="case-tags">
                <span v-for="tag in caseData.tags" :key="tag.id" class="tag-chip">{{ tag.name }}</span>
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

const descText = computed(() => {
    const parts: string[] = []
    if (caseData.value.tags?.length) {
        parts.push(`分类：${caseData.value.tags.map(t => t.name).join('、')}`)
    }
    parts.push(`共 ${caseData.value.event_count} 个事件节点，${caseData.value.source_count} 个来源`)
    return parts.join('。')
})

function fromNow(dateStr: string) {
    return dayjs(dateStr).fromNow()
}
</script>

<style scoped>
.case-card-link {
    text-decoration: none;
    display: block;
}

.case-card {
    padding: 20px 0;
    border-bottom: 1px solid #f3f4f6;
    cursor: pointer;
    transition: background 0.15s;
}

.case-card:hover {
    background: #fafbfc;
    margin: 0 -16px;
    padding: 20px 16px;
    border-radius: 8px;
}

.case-title {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 8px;
    line-height: 1.4;
}

.case-card:hover .case-title {
    color: #ef4444;
}

.case-desc {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.7;
    margin: 0 0 10px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Meta row */
.case-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 13px;
    color: #9ca3af;
}

.meta-left {
    display: flex;
    align-items: center;
    gap: 6px;
}

.meta-hotness {
    display: flex;
    align-items: center;
    gap: 2px;
    color: #ef4444;
    font-weight: 600;
}

.hotness-icon {
    font-size: 14px;
}

.meta-sep {
    color: #d1d5db;
}

.meta-time {
    color: #9ca3af;
}

.meta-tracking {
    color: #2563eb;
    font-size: 12px;
}

.meta-right {
    display: flex;
    gap: 8px;
}

.event-badge,
.source-badge {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #f3f4f6;
    color: #6b7280;
}

/* Tags */
.case-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.tag-chip {
    font-size: 12px;
    padding: 2px 10px;
    background: #fef2f2;
    color: #ef4444;
    border-radius: 4px;
    font-weight: 500;
}
</style>
