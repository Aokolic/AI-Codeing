<template>
    <div class="admin-page">
        <!-- Admin dashboard -->
        <div class="admin-header">
            <div class="admin-title">
                <span>📡</span>
                <span class="admin-title-text">数据源管理</span>
                <span v-if="feeds.length" class="admin-title-badge">{{ feeds.length }} 个来源</span>
            </div>
            <div class="header-actions">
                <n-button type="primary" @click="showCreateModal = true">+ 添加数据源</n-button>
            </div>
        </div>

        <!-- Feed list -->
        <div v-if="feedsLoading" class="loading-section"><n-spin /></div>
        <div v-else-if="feeds.length" class="feeds-list">
            <feed-status-panel v-for="feed in feeds" :key="feed.id" :feed="feed" @collected="handleCollected"
                @edit="handleEditFeed" @delete="handleDeleteFeed" />
        </div>
        <n-empty v-else description="暂无数据源，点击「添加数据源」开始配置" />

        <!-- Pagination -->
        <div v-if="feedTotal > feedPageSize" class="pagination">
            <n-pagination v-model:page="feedPage" :page-count="feedPageCount" @update:page="loadFeeds" />
        </div>

        <!-- Create / Edit feed modal -->
        <n-modal v-model:show="showCreateModal" title="添加数据源" preset="card" style="max-width: 480px;">
            <n-form :model="feedForm" @submit.prevent="handleSaveFeed">
                <n-form-item label="名称 *"><n-input v-model:value="feedForm.name"
                        :disabled="isEditingBuiltin" /></n-form-item>
                <n-form-item label="类型 *">
                    <n-select v-model:value="feedForm.feed_type" :options="feedTypeOptions"
                        :disabled="isEditingBuiltin" />
                </n-form-item>
                <n-form-item label="URL *"><n-input v-model:value="feedForm.url"
                        :disabled="isEditingBuiltin" /></n-form-item>
                <n-form-item label="Cron计划">
                    <n-input v-model:value="feedForm.schedule_cron" placeholder="*/30 * * * *"
                        :disabled="isEditingBuiltin" />
                </n-form-item>
                <div class="modal-footer">
                    <n-button @click="showCreateModal = false">取消</n-button>
                    <n-button type="primary" attr-type="submit" :loading="savingFeed">保存</n-button>
                </div>
            </n-form>
        </n-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
    NForm, NFormItem, NInput, NButton, NModal, NSelect, NEmpty, NSpin, NPagination, useMessage,
} from 'naive-ui'
import FeedStatusPanel from '@/components/FeedStatusPanel.vue'
import { listFeeds, createFeed, updateFeed, deleteFeed } from '@/api/feeds'
import type { DataFeedOut, DataFeedCreate } from '@/types'

const message = useMessage()

// Feeds
const feeds = ref<DataFeedOut[]>([])
const feedsLoading = ref(false)
const feedPage = ref(1)
const feedPageSize = 10
const feedTotal = ref(0)
const feedPageCount = computed(() => Math.ceil(feedTotal.value / feedPageSize))
const showCreateModal = ref(false)
const editingFeedId = ref<string | null>(null)
const savingFeed = ref(false)

const isEditingBuiltin = computed(() => {
    if (!editingFeedId.value) return false
    const feed = feeds.value.find((f) => f.id === editingFeedId.value)
    return feed?.is_builtin ?? false
})

const emptyFeedForm = (): DataFeedCreate => ({
    name: '',
    feed_type: 'rss',
    url: '',
    schedule_cron: '0 2 * * *',
})
const feedForm = ref<DataFeedCreate>(emptyFeedForm())

const feedTypeOptions = [
    { label: 'RSS', value: 'rss' },
    { label: 'Atom', value: 'atom' },
    { label: 'Web Scraper', value: 'web_scraper' },
    { label: 'API', value: 'api' },
]

async function loadFeeds() {
    feedsLoading.value = true
    try {
        const res = await listFeeds(feedPage.value, feedPageSize)
        feeds.value = res.items
        feedTotal.value = res.total
    } finally {
        feedsLoading.value = false
    }
}

async function handleSaveFeed() {
    savingFeed.value = true
    try {
        if (editingFeedId.value) {
            await updateFeed(editingFeedId.value, feedForm.value)
        } else {
            await createFeed(feedForm.value)
        }
        showCreateModal.value = false
        feedForm.value = emptyFeedForm()
        editingFeedId.value = null
        loadFeeds()
    } finally {
        savingFeed.value = false
    }
}

function handleEditFeed(id: string) {
    const feed = feeds.value.find((f) => f.id === id)
    if (!feed) return
    editingFeedId.value = id
    feedForm.value = {
        name: feed.name,
        feed_type: feed.feed_type,
        url: feed.url,
        schedule_cron: feed.schedule_cron,
    }
    showCreateModal.value = true
}

async function handleDeleteFeed(id: string) {
    await deleteFeed(id)
    loadFeeds()
}

async function handleCollected() {
    loadFeeds()
}

onMounted(() => {
    loadFeeds()
})
</script>

<style scoped>
.admin-page {
    max-width: 900px;
    margin: 0 auto;
}

/* Dashboard */
.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 16px 20px;
    background: #fff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(15, 23, 42, .05);
}

.admin-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.admin-title-text {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

.admin-title-badge {
    font-size: 11px;
    padding: 2px 8px;
    background: #ede9fe;
    color: #4f46e5;
    border-radius: 999px;
    font-weight: 600;
}

.header-actions {
    display: flex;
    gap: 8px;
}

.feeds-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.loading-section {
    display: flex;
    justify-content: center;
    padding: 60px;
}

.pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
}
</style>
