<template>
    <span class="cred-badge" :class="`level-${level}`" :data-level="level">
        <span class="dot"></span>
        {{ labelMap[level] }}
        <span v-if="score !== undefined" class="score">{{ Math.round(score) }}</span>
    </span>
</template>

<script setup lang="ts">
import type { CredibilityLevel } from '@/types'

defineProps<{
    level: CredibilityLevel
    score?: number
}>()

const labelMap: Record<CredibilityLevel, string> = {
    high: '高可信',
    medium: '中可信',
    low: '低可信',
    unverified: '未核实',
}
</script>

<style scoped>
.cred-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px 2px 6px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}

.score {
    font-variant-numeric: tabular-nums;
    opacity: 0.8;
}

.level-high {
    background: #d1fae5;
    color: #065f46;
}

.level-high .dot {
    background: #059669;
}

.level-medium {
    background: #ede9fe;
    color: #5b21b6;
}

.level-medium .dot {
    background: #7c3aed;
}

.level-low {
    background: #fef3c7;
    color: #92400e;
}

.level-low .dot {
    background: #d97706;
}

.level-unverified {
    background: #fee2e2;
    color: #991b1b;
}

.level-unverified .dot {
    background: #dc2626;
}
</style>
