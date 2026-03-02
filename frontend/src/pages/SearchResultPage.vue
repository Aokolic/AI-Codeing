<template>
    <div class="search-result-page">
        <div class="search-header">
            <search-bar :initial-query="query" @search="handleSearch" />
        </div>

        <template v-if="query">
            <p class="result-info" v-if="!loading">
                <span class="result-count">{{ results.length }}</span>
                <span class="result-sep">|</span>
                <span>搜索「<span class="result-keyword">{{ query }}</span>」的结果</span>
            </p>

            <div v-if="loading" class="grid-loading">
                <n-skeleton v-for="i in 4" :key="i" height="110px" style="margin-bottom:12px;" />
            </div>

            <n-empty v-else-if="!results.length" description="未找到相关案例">
                <template #extra>
                    <p class="empty-hint">你可以尝试浏览<router-link to="/">热门案例</router-link></p>
                </template>
            </n-empty>

            <div v-else class="results-list">
                <case-card v-for="c in results" :key="c.id" :case="c" />
            </div>
        </template>

        <n-empty v-else description="请输入关键词搜索案例" />
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NEmpty, NSkeleton } from 'naive-ui'
import SearchBar from '@/components/SearchBar.vue'
import CaseCard from '@/components/CaseCard.vue'
import { searchCases } from '@/api/cases'
import type { CaseSummary, SearchSuggestedCase } from '@/types'

function toSummary(c: SearchSuggestedCase): CaseSummary {
    return {
        id: c.id,
        title: c.title,
        status: c.status,
        hotness_score: 0,
        tags: [],
        event_count: c.event_count,
        source_count: 0,
        created_at: new Date().toISOString(),
        last_event_at: null,
    }
}

const route = useRoute()
const router = useRouter()
const query = ref((route.query.q as string) ?? '')
const results = ref<CaseSummary[]>([])
const loading = ref(false)

async function doSearch(q: string) {
    if (!q.trim()) return
    loading.value = true
    try {
        results.value = (await searchCases(q, 20)).map(toSummary)
    } finally {
        loading.value = false
    }
}

function handleSearch(q: string) {
    query.value = q
    router.replace({ query: { q } })
}

watch(query, (q) => { if (q) doSearch(q) })
watch(() => route.query.q, (q) => { query.value = (q as string) ?? '' })

onMounted(() => { if (query.value) doSearch(query.value) })
</script>

<style scoped>
.search-result-page {
    max-width: 900px;
    margin: 0 auto;
}

.search-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);
    margin: -28px -24px 0;
    padding: 32px 40px 28px;
    margin-bottom: 24px;
}

.result-info {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: #64748b;
    margin-bottom: 16px;
    padding: 10px 14px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.result-count {
    font-size: 20px;
    font-weight: 700;
    color: #4f46e5;
    line-height: 1;
}

.result-sep {
    color: #e2e8f0;
}

.result-keyword {
    font-weight: 600;
    color: #0f172a;
    background: #f0f4ff;
    padding: 2px 8px;
    border-radius: 4px;
}

.results-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.empty-hint {
    font-size: 13px;
    color: #94a3b8;
}

.empty-hint a {
    color: #4f46e5;
    text-decoration: underline;
}

@media (max-width: 640px) {
    .search-header {
        margin: -16px -16px 16px;
        padding: 24px 20px;
    }
}
</style>
