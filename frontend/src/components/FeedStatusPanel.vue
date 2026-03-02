<template>
    <div class="feed-status-panel">
        <div class="feed-info">
            <div class="feed-name">{{ feed.name }}</div>
            <div class="feed-meta">
                <n-tag :type="statusTagType" size="small" :bordered="false" :data-status="feed.status">
                    {{ statusLabel }}
                </n-tag>
                <span v-if="feed.consecutive_failures > 0" class="failures">
                    连续失败 {{ feed.consecutive_failures }} 次
                </span>
                <span v-if="feed.last_collected_at" class="last-time">
                    上次采集：{{ formatTime(feed.last_collected_at) }}
                </span>
            </div>
            <div class="feed-url">{{ feed.url }}</div>
        </div>
        <div class="feed-actions">
            <n-button size="small" :loading="collecting" data-testid="collect-btn" @click="handleCollect">
                立即采集
            </n-button>
            <n-button size="small" quaternary @click="emit('edit', feed.id)">
                编辑
            </n-button>
            <n-button size="small" quaternary type="error" @click="emit('delete', feed.id)">
                删除
            </n-button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NTag, NButton } from 'naive-ui'
import dayjs from 'dayjs'
import type { DataFeedOut } from '@/types'

const props = defineProps<{ feed: DataFeedOut }>()
const emit = defineEmits<{
    (e: 'collect', id: string): void
    (e: 'edit', id: string): void
    (e: 'delete', id: string): void
}>()

const collecting = ref(false)

async function handleCollect() {
    collecting.value = true
    try {
        emit('collect', props.feed.id)
    } finally {
        // Parent handles async; reset after brief feedback
        setTimeout(() => { collecting.value = false }, 500)
    }
}

const statusLabelMap: Record<string, string> = {
    normal: '正常',
    warning: '警告',
    offline: '离线',
    paused: '暂停',
}
const statusLabel = computed(() => statusLabelMap[props.feed.status] ?? props.feed.status)

const statusTagType = computed(() => {
    const map: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
        normal: 'success',
        warning: 'warning',
        offline: 'error',
        paused: 'default',
    }
    return map[props.feed.status] ?? 'default'
})

function formatTime(t: string) {
    return dayjs(t).format('MM-DD HH:mm')
}
</script>

<style scoped>
.feed-status-panel {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background: #fff;
    box-shadow: 0 1px 3px rgba(15, 23, 42, .04);
    transition: box-shadow 0.15s;
}

.feed-status-panel:hover {
    box-shadow: 0 2px 8px rgba(15, 23, 42, .08);
}

.feed-name {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 5px;
}

.feed-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #64748b;
    margin-bottom: 3px;
}

.failures {
    color: #dc2626;
    font-weight: 500;
    background: #fee2e2;
    padding: 0 6px;
    border-radius: 4px;
}

.last-time {
    color: #94a3b8;
}

.feed-url {
    font-size: 11px;
    color: #94a3b8;
    word-break: break-all;
    font-family: 'Courier New', monospace;
}

.feed-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
}
</style>
