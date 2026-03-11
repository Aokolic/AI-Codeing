<template>
    <div class="home-page">
        <!-- Tab navigation -->
        <div class="tab-nav">
            <button class="tab-btn" :class="{ active: activeTab === 'hot' }" @click="activeTab = 'hot'">热点</button>
            <button class="tab-btn" :class="{ active: activeTab === 'track' }" @click="activeTab = 'track'">跟踪</button>
        </div>

        <!-- Featured cases (top hot cases as large cards) -->
        <div v-if="activeTab === 'hot' && featuredCases.length" class="featured-section">
            <div class="featured-grid">
                <router-link v-for="c in featuredCases" :key="c.id" :to="`/cases/${c.id}`" class="featured-card">
                    <div class="featured-overlay">
                        <span class="featured-time">{{ fromNow(c.created_at) }}</span>
                        <span class="featured-count">{{ c.event_count }}</span>
                    </div>
                    <h3 class="featured-title">{{ c.title }}</h3>
                </router-link>
            </div>
        </div>

        <!-- Case list -->
        <div v-if="loading" class="cases-loading">
            <div v-for="i in 4" :key="i" class="skeleton-item">
                <div class="skel-title shimmer"></div>
                <div class="skel-desc shimmer"></div>
                <div class="skel-meta shimmer"></div>
            </div>
        </div>
        <n-empty v-else-if="!displayCases.length" description="暂无相关案例" />
        <div v-else class="case-list">
            <case-card v-for="c in displayCases" :key="c.id" :case="c" />
        </div>

        <!-- Pagination -->
        <div v-if="total > pageSize" class="pagination">
            <n-pagination v-model:page="page" :page-count="pageCount" @update:page="loadCases" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NEmpty, NPagination } from 'naive-ui'
import CaseCard from '@/components/CaseCard.vue'
import { listCases } from '@/api/cases'
import type { CaseSummary } from '@/types'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const router = useRouter()
const cases = ref<CaseSummary[]>([])
const loading = ref(false)
const activeTab = ref<'hot' | 'track'>('hot')
const page = ref(1)
const pageSize = 12
const total = ref(0)
const pageCount = computed(() => Math.ceil(total.value / pageSize))

// Top 3 hot cases as featured cards
const featuredCases = computed(() => cases.value.slice(0, 3))

// Remaining cases for list view
const displayCases = computed(() => {
    if (activeTab.value === 'hot') {
        return cases.value.slice(3)
    }
    return cases.value.filter(c => c.status === 'active')
})

function fromNow(dateStr: string) {
    return dayjs(dateStr).fromNow()
}

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

function handleSearch(q: string) {
    router.push({ path: '/search', query: { q } })
}

onMounted(() => {
    loadCases()
})
</script>

<style scoped>
.home-page {
    max-width: 960px;
    margin: 0 auto;
}

/* Tab navigation */
.tab-nav {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 24px;
}

.tab-btn {
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 500;
    color: #9ca3af;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:hover {
    color: #374151;
}

.tab-btn.active {
    color: #ef4444;
    border-bottom-color: #ef4444;
    font-weight: 600;
}

/* Featured section */
.featured-section {
    margin-bottom: 32px;
}

.featured-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.featured-card {
    position: relative;
    background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px;
    padding: 0;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    overflow: hidden;
    text-decoration: none;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.featured-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.featured-overlay {
    position: absolute;
    top: 16px;
    left: 16px;
    right: 16px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.featured-time {
    background: #ef4444;
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 4px;
}

.featured-count {
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.featured-title {
    padding: 20px 16px 16px;
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    line-height: 1.4;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
}

/* Case list */
.case-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* Skeleton loading */
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

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    margin-top: 32px;
    padding-bottom: 24px;
}

@media (max-width: 640px) {
    .featured-grid {
        grid-template-columns: 1fr;
    }

    .tab-btn {
        padding: 10px 16px;
        font-size: 14px;
    }
}
</style>
