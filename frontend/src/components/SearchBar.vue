<template>
    <div class="search-bar" :class="{ compact }">
        <n-input v-model:value="query" :placeholder="compact ? '搜索…' : '搜索案例、事件、关键词…'" clearable
            :size="compact ? 'small' : 'medium'" @keydown.enter="handleSearch" @clear="handleClear">
            <template #prefix>
                <n-icon>
                    <SearchOutline />
                </n-icon>
            </template>
            <template #suffix>
                <n-button text size="small" data-testid="search-btn" @click="handleSearch">
                    搜索
                </n-button>
            </template>
        </n-input>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NInput, NButton, NIcon } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'

const props = withDefaults(defineProps<{
    compact?: boolean
    initialQuery?: string
}>(), { compact: false, initialQuery: '' })

const emit = defineEmits<{
    (e: 'search', query: string): void
}>()

const query = ref(props.initialQuery)

function handleSearch() {
    const q = query.value.trim()
    if (q) emit('search', q)
}

function handleClear() {
    query.value = ''
}

// expose for parent sync
defineExpose({ query })
</script>

<style scoped>
.search-bar {
    width: 100%;
}

.search-bar.compact {
    max-width: 240px;
}
</style>
