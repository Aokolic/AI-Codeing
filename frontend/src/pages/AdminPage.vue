<template>
    <div class="admin-page">
        <!-- Login gate -->
        <div v-if="!isLoggedIn" class="login-card">
            <div class="login-logo">
                <span class="login-logo-icon">⚡</span>
                <span class="login-logo-title">管理控制台</span>
                <span class="login-logo-sub">后真相时代 · 信息甄别平台</span>
            </div>
            <n-form @submit.prevent="handleLogin">
                <n-form-item label="用户名">
                    <n-input v-model:value="loginForm.username" placeholder="admin" size="large" />
                </n-form-item>
                <n-form-item label="密码">
                    <n-input v-model:value="loginForm.password" type="password" show-password-on="click" size="large" />
                </n-form-item>
                <n-button attr-type="submit" type="primary" :loading="loginLoading" block size="large"
                    style="margin-top: 4px;">登录</n-button>
                <p v-if="loginError" class="login-error">{{ loginError }}</p>
            </n-form>
        </div>

        <!-- Admin dashboard -->
        <template v-else>
            <div class="admin-header">
                <div class="admin-title">
                    <span>📡</span>
                    <span class="admin-title-text">数据源管理</span>
                    <span v-if="feeds.length" class="admin-title-badge">{{ feeds.length }} 个来源</span>
                </div>
                <div class="header-actions">
                    <n-button type="primary" @click="showCreateModal = true">+ 添加数据源</n-button>
                    <n-button quaternary @click="handleLogout">退出登录</n-button>
                </div>
            </div>

            <!-- Feed list -->
            <div v-if="feedsLoading" class="loading-section"><n-spin /></div>
            <div v-else-if="feeds.length" class="feeds-list">
                <feed-status-panel v-for="feed in feeds" :key="feed.id" :feed="feed" @collect="handleCollect"
                    @edit="handleEditFeed" @delete="handleDeleteFeed" />
            </div>
            <n-empty v-else description="暂无数据源，点击「添加数据源」开始配置" />

            <!-- Pagination -->
            <div v-if="feedTotal > feedPageSize" class="pagination">
                <n-pagination v-model:page="feedPage" :page-count="feedPageCount" @update:page="loadFeeds" />
            </div>
        </template>

        <!-- Create / Edit feed modal -->
        <n-modal v-model:show="showCreateModal" title="添加数据源" preset="card" style="max-width: 480px;">
            <n-form :model="feedForm" @submit.prevent="handleSaveFeed">
                <n-form-item label="名称 *"><n-input v-model:value="feedForm.name" /></n-form-item>
                <n-form-item label="类型 *">
                    <n-select v-model:value="feedForm.feed_type" :options="feedTypeOptions" />
                </n-form-item>
                <n-form-item label="URL *"><n-input v-model:value="feedForm.url" /></n-form-item>
                <n-form-item label="Cron计划">
                    <n-input v-model:value="feedForm.schedule_cron" placeholder="0 2 * * *" />
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
    NForm, NFormItem, NInput, NButton, NModal, NSelect, NEmpty, NSpin, NPagination,
} from 'naive-ui'
import FeedStatusPanel from '@/components/FeedStatusPanel.vue'
import { login, logout } from '@/api/auth'
import { listFeeds, createFeed, updateFeed, deleteFeed, triggerCollect } from '@/api/feeds'
import { hasToken } from '@/api/client'
import type { DataFeedOut, DataFeedCreate } from '@/types'

// Auth
const isLoggedIn = ref(hasToken())
const loginForm = ref({ username: '', password: '' })
const loginLoading = ref(false)
const loginError = ref('')

async function handleLogin() {
    loginLoading.value = true
    loginError.value = ''
    try {
        await login({ username: loginForm.value.username, password: loginForm.value.password })
        isLoggedIn.value = true
        loadFeeds()
    } catch (e: unknown) {
        loginError.value = e instanceof Error ? e.message : '登录失败'
    } finally {
        loginLoading.value = false
    }
}

function handleLogout() {
    logout()
    isLoggedIn.value = false
}

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

async function handleCollect(id: string) {
    await triggerCollect(id)
}

onMounted(() => {
    if (isLoggedIn.value) loadFeeds()
})
</script>

<style scoped>
.admin-page {
    max-width: 900px;
    margin: 0 auto;
}

/* Login card */
.login-card {
    max-width: 420px;
    margin: 60px auto;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 40px rgba(15, 23, 42, .12);
    padding: 40px;
    border: 1px solid #e2e8f0;
}

.login-logo {
    text-align: center;
    margin-bottom: 28px;
}

.login-logo-icon {
    font-size: 36px;
    display: block;
    margin-bottom: 8px;
}

.login-logo-title {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    display: block;
    margin-bottom: 4px;
}

.login-logo-sub {
    font-size: 13px;
    color: #94a3b8;
}

.login-error {
    color: #dc2626;
    font-size: 13px;
    margin-top: 10px;
    padding: 8px 12px;
    background: #fee2e2;
    border-radius: 6px;
    text-align: center;
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
