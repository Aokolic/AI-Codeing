<template>
    <div class="search-result-page">
        <!-- Search title area -->
        <div class="search-title-area">
            <div class="search-title-row">
                <h2 class="search-title" v-if="query">
                    搜索「<span class="search-keyword">{{ query }}</span>」
                </h2>
                <h2 class="search-title" v-else>搜索案例</h2>
            </div>
            <div class="search-input-row">
                <search-bar :initial-query="query" @search="handleSearch" />
            </div>
        </div>

        <template v-if="query">
            <!-- Result info -->
            <p class="result-info" v-if="!loading && results.length">
                <span class="result-count">{{ results.length }}</span>
                <span class="result-text">条相关结果</span>
            </p>

            <!-- Loading skeleton -->
            <div v-if="loading" class="cases-loading">
                <div v-for="i in 4" :key="i" class="skeleton-item">
                    <div class="skel-title shimmer"></div>
                    <div class="skel-desc shimmer"></div>
                    <div class="skel-meta shimmer"></div>
                </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="!results.length" class="empty-state">
                <div class="empty-icon">🔍</div>
                <p class="empty-title">未找到与「{{ query }}」相关的案例</p>
                <p class="empty-hint">试试其他关键词，或<router-link to="/" class="empty-link">浏览热门案例</router-link></p>
            </div>

            <!-- Results list -->
            <div v-else class="case-list">
                <case-card v-for="c in results" :key="c.id" :case="c" />
            </div>
        </template>

        <!-- No query state -->
        <div v-else class="empty-state">
            <div class="empty-icon">🔎</div>
            <p class="empty-title">输入关键词搜索案例</p>
            <p class="empty-hint">支持按标题、描述内容搜索</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SearchBar from '@/components/SearchBar.vue'
import CaseCard from '@/components/CaseCard.vue'
import { searchCases } from '@/api/cases'
import type { CaseSummary } from '@/types'

const route = useRoute()
const router = useRouter()
const query = ref((route.query.q as string) ?? '')
const results = ref<CaseSummary[]>([])
const loading = ref(false)

async function doSearch(q: string) {
    if (!q.trim()) return
    loading.value = true
    try {
        results.value = await searchCases(q, 20)
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
    max-width: 960px;
    margin: 0 auto;
}

/* ── Search title area ── */
.search-title-area {
    padding-bottom: 20px;
    margin-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
}

.search-title-row {
    margin-bottom: 16px;
}

.search-title {
    font-size: 22px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
    line-height: 1.4;
}

.search-keyword {
    color: #ef4444;
}

.search-input-row {
    max-width: 560px;
}

/* ── Result info ── */
.result-info {
    display: flex;
    align-items: baseline;
    gap: 6px;
    font-size: 14px;
    color: #9ca3af;
    margin: 0 0 12px;
}

.result-count {
    font-size: 18px;
    font-weight: 700;
    color: #ef4444;
    line-height: 1;
}

.result-text {
    color: #6b7280;
}

/* ── Card list (match HomePage) ── */
.case-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* ── Skeleton loading (match HomePage) ── */
.cases-loading {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.skeleton-item {
    padding: 20px 0;
    border-bottom: 1px solid #f3f4f6;
}

.skel-title {
    height: 20px;
    width: 60%;
    border-radius: 4px;
    margin-bottom: 10px;
}

.skel-desc {
    height: 14px;
    width: 90%;
    border-radius: 4px;
    margin-bottom: 8px;
}

.skel-meta {
    height: 12px;
    width: 40%;
    border-radius: 4px;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.empty-title {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px;
}

.empty-hint {
    font-size: 14px;
    color: #9ca3af;
    margin: 0;
}

.empty-link {
    color: #ef4444;
    text-decoration: none;
    font-weight: 500;
}

.empty-link:hover {
    text-decoration: underline;
}

@media (max-width: 640px) {
    .search-title {
        font-size: 18px;
    }

    .search-input-row {
        max-width: 100%;
    }
}
</style>
