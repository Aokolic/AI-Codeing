<template>
    <div class="home-page">
        <!-- Hero -->
        <div class="hero-section">
            <div class="hero-badge">⚡ 实时信息甄别系统</div>
            <h1 class="hero-title">追踪信息，揭示真相</h1>
            <p class="hero-sub">聚合多方来源 · 时间线追踪 · 三维可信度评估</p>
            <search-bar class="hero-search" @search="handleSearch" />
            <div class="hero-stats">
                <span class="hstat">📋 {{ total }} 个追踪案例</span>
                <span class="hstat-sep">·</span>
                <span class="hstat">🏷 {{ tags.length }} 个分类</span>
            </div>
        </div>

        <!-- Tag filter -->
        <div class="tag-filter">
            <button class="tag-pill" :class="{ active: selectedTagId === null }"
                @click="selectedTagId = null">全部</button>
            <button v-for="tag in tags" :key="tag.id" class="tag-pill" :class="{ active: selectedTagId === tag.id }"
                @click="selectedTagId = tag.id">
                {{ tag.name }} <span class="tag-count">{{ tag.case_count }}</span>
            </button>
        </div>

        <!-- Hot cases grid -->
        <div v-if="loading" class="cases-grid">
            <div v-for="i in 6" :key="i" class="skeleton-card">
                <div class="skel-bar"></div>
                <div class="skel-body">
                    <div class="skel-title shimmer"></div>
                    <div class="skel-meta shimmer"></div>
                    <div class="skel-tags shimmer"></div>
                </div>
            </div>
        </div>
        <n-empty v-else-if="!filteredCases.length" description="暂无相关案例" />
        <div v-else class="cases-grid">
            <case-card v-for="c in filteredCases" :key="c.id" :case="c" />
        </div>

        <!-- Pagination -->
        <div v-if="total > pageSize" class="pagination">
            <n-pagination v-model:page="page" :page-count="pageCount" @update:page="loadCases" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NEmpty, NPagination } from 'naive-ui'
import SearchBar from '@/components/SearchBar.vue'
import CaseCard from '@/components/CaseCard.vue'
import { listCases, listTags } from '@/api/cases'
import type { CaseSummary, TagWithCount } from '@/types'

const router = useRouter()
const cases = ref<CaseSummary[]>([])
const tags = ref<TagWithCount[]>([])
const loading = ref(false)
const selectedTagId = ref<string | null>(null)
const page = ref(1)
const pageSize = 12
const total = ref(0)
const pageCount = computed(() => Math.ceil(total.value / pageSize))

const filteredCases = computed(() =>
    selectedTagId.value
        ? cases.value.filter((c) => c.tags?.some((t) => t.id === selectedTagId.value))
        : cases.value,
)

async function loadCases() {
    loading.value = true
    try {
        const res = await listCases({ page: page.value, page_size: pageSize })
        cases.value = res.items
        total.value = res.total
    } finally {
        loading.value = false
    }
}

async function loadTags() {
    try {
        tags.value = await listTags()
    } catch { /* non-critical */ }
}

function handleSearch(q: string) {
    router.push({ path: '/search', query: { q } })
}

watch(selectedTagId, () => { page.value = 1 })

onMounted(() => {
    loadCases()
    loadTags()
})
</script>

<style scoped>
.home-page {
    max-width: 1100px;
    margin: 0 auto;
}

/* Hero */
.hero-section {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    margin: -28px -24px 0;
    padding: 56px 40px 44px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 100%, rgba(99, 102, 241, .25) 0%, transparent 70%);
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    background: rgba(99, 102, 241, .2);
    border: 1px solid rgba(129, 140, 248, .3);
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 999px;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    color: #e0e7ff;
    letter-spacing: -0.03em;
    margin: 0 0 10px;
    text-shadow: 0 2px 16px rgba(79, 70, 229, .4);
}

.hero-sub {
    font-size: 15px;
    color: #a5b4fc;
    margin: 0 0 24px;
}

.hero-search {
    max-width: 540px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.hero-stats {
    margin-top: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    color: #818cf8;
}

.hstat-sep {
    color: #4338ca;
}

/* Tag filter */
.tag-filter {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 20px 0 16px;
    padding: 0 2px;
}

.tag-pill {
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid #e2e8f0;
    background: #fff;
    color: #64748b;
    cursor: pointer;
    transition: all 0.15s;
}

.tag-pill:hover {
    border-color: #6366f1;
    color: #4f46e5;
    background: #f0f4ff;
}

.tag-pill.active {
    background: #4f46e5;
    color: #fff;
    border-color: #4f46e5;
}

.tag-count {
    font-size: 10px;
    opacity: 0.65;
    margin-left: 2px;
}

/* Skeleton cards */
.skeleton-card {
    display: flex;
    overflow: hidden;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(15, 23, 42, .07);
}

.skel-bar {
    width: 4px;
    background: #e2e8f0;
}

.skel-body {
    flex: 1;
    padding: 14px 16px;
}

.skel-title {
    height: 16px;
    border-radius: 4px;
    margin-bottom: 10px;
    width: 75%;
}

.skel-meta {
    height: 11px;
    border-radius: 4px;
    margin-bottom: 8px;
    width: 50%;
}

.skel-tags {
    height: 18px;
    border-radius: 999px;
    width: 35%;
}

/* Grid */
.cases-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 14px;
    margin-bottom: 8px;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    margin-top: 28px;
}

@media (max-width: 640px) {
    .hero-section {
        padding: 36px 20px 32px;
        margin: -16px -16px 0;
    }

    .hero-title {
        font-size: 22px;
    }

    .cases-grid {
        grid-template-columns: 1fr;
    }
}
</style>
