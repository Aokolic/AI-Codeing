<template>
    <div class="credibility-panel">
        <!-- Overall score hero -->
        <div class="score-hero">
            <div class="score-ring" :class="`ring-${detail.level}`">
                <span class="score-num">{{ Math.round(detail.total_score) }}</span>
                <span class="score-denom">/100</span>
            </div>
            <div class="score-info">
                <div class="score-label">综合可信度</div>
                <credibility-badge :level="detail.level" :score="detail.total_score" />
                <div class="score-time">{{ dayjs(detail.assessed_at).format('YYYY-MM-DD HH:mm') }} 评估</div>
            </div>
        </div>

        <!-- Conflict warning -->
        <div v-if="detail.has_conflict" class="conflict-alert">
            <div>
                <div class="conflict-title">⚠ 来源分歧（{{ detail.conflict_sources?.length ?? 0 }} 个冲突来源）</div>
                <div class="conflict-desc">不同来源的报道存在实质性矛盾，建议交叉核实后谨慎参考。</div>
            </div>
        </div>

        <!-- Dimension scores -->
        <div class="dimensions">
            <div class="dim-item">
                <div class="dim-header">
                    <span class="dim-name">⭐ 权威性</span>
                    <span class="dim-score" :class="scoreClass(detail.authority_score)">{{
                        Math.round(detail.authority_score) }}</span>
                </div>
                <div class="dim-bar">
                    <div class="dim-fill authority" :style="{ width: detail.authority_score + '%' }"></div>
                </div>
                <p v-if="detail.scoring_explanation?.authority" class="dim-explain">{{
                    detail.scoring_explanation.authority }}</p>
            </div>
            <div class="dim-item">
                <div class="dim-header">
                    <span class="dim-name">⏱ 时效性</span>
                    <span class="dim-score" :class="scoreClass(detail.timeliness_score)">{{
                        Math.round(detail.timeliness_score) }}</span>
                </div>
                <div class="dim-bar">
                    <div class="dim-fill timeliness" :style="{ width: detail.timeliness_score + '%' }"></div>
                </div>
                <p v-if="detail.scoring_explanation?.timeliness" class="dim-explain">{{
                    detail.scoring_explanation.timeliness }}</p>
            </div>
            <div class="dim-item">
                <div class="dim-header">
                    <span class="dim-name">🔗 交叉验证</span>
                    <span class="dim-score" :class="scoreClass(detail.cross_verify_score)">{{
                        Math.round(detail.cross_verify_score) }}</span>
                </div>
                <div class="dim-bar">
                    <div class="dim-fill cross-verify" :style="{ width: detail.cross_verify_score + '%' }"></div>
                </div>
                <p v-if="detail.scoring_explanation?.cross_verify" class="dim-explain">{{
                    detail.scoring_explanation.cross_verify }}</p>
            </div>
        </div>

        <!-- Sources -->
        <template v-if="detail.sources?.length">
            <div class="sources-header">来源列表 <span class="sources-count">{{ detail.sources.length }}</span></div>
            <n-data-table :columns="sourceColumns" :data="detail.sources" size="small" :pagination="false"
                class="sources-table" />
        </template>
    </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { NDataTable } from 'naive-ui'
import CredibilityBadge from './CredibilityBadge.vue'
import dayjs from 'dayjs'
import type { CredibilityDetail, CredibilityLevel } from '@/types'

defineProps<{ detail: CredibilityDetail }>()

function scoreClass(score: number) {
    if (score >= 70) return 'score-high'
    if (score >= 40) return 'score-medium'
    return 'score-low'
}

const sourceColumns = [
    { title: '来源', key: 'name' },
    { title: '类型', key: 'source_type', width: 72 },
    {
        title: '可信度',
        key: 'credibility_level',
        width: 82,
        render: (row: { credibility_level: CredibilityLevel }) =>
            h(CredibilityBadge, { level: row.credibility_level }),
    },
    {
        title: '发布时间',
        key: 'published_at',
        width: 110,
        render: (row: { published_at: string | null }) =>
            row.published_at ? dayjs(row.published_at).format('MM-DD HH:mm') : '—'
    },
]
</script>

<style scoped>
.credibility-panel {
    padding: 4px 0;
}

/* Score hero */
.score-hero {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 10px;
    margin-bottom: 16px;
    border: 1px solid #e2e8f0;
}

.score-ring {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    border: 4px solid #e2e8f0;
    flex-shrink: 0;
}

.ring-high {
    border-color: #059669;
    color: #065f46;
}

.ring-medium {
    border-color: #2563eb;
    color: #1e40af;
}

.ring-low {
    border-color: #d97706;
    color: #92400e;
}

.ring-unverified {
    border-color: #dc2626;
    color: #991b1b;
}

.score-num {
    font-size: 24px;
    line-height: 1;
}

.score-denom {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 400;
}

.score-info {
    flex: 1;
}

.score-label {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 6px;
}

.score-time {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 6px;
}

/* Conflict alert */
.conflict-alert {
    display: flex;
    gap: 10px;
    padding: 12px 16px;
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 8px;
    margin-bottom: 16px;
}

.conflict-title {
    font-size: 13px;
    font-weight: 600;
    color: #9f1239;
    margin-bottom: 3px;
}

.conflict-desc {
    font-size: 12px;
    color: #be123c;
}

/* Dimension scores */
.dimensions {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 20px;
}

.dim-item {}

.dim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.dim-name {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
}

.dim-score {
    font-size: 13px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}

.score-high {
    color: #059669;
}

.score-medium {
    color: #2563eb;
}

.score-low {
    color: #d97706;
}

.dim-bar {
    height: 6px;
    background: #f1f5f9;
    border-radius: 999px;
    overflow: hidden;
}

.dim-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}

.authority {
    background: linear-gradient(90deg, #10b981, #059669);
}

.timeliness {
    background: linear-gradient(90deg, #60a5fa, #2563eb);
}

.cross-verify {
    background: linear-gradient(90deg, #a78bfa, #7c3aed);
}

.dim-explain {
    font-size: 11px;
    color: #94a3b8;
    margin: 4px 0 0;
}

/* Sources */
.sources-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #e2e8f0;
}

.sources-count {
    background: #e0e7ff;
    color: #4f46e5;
    font-size: 11px;
    padding: 1px 7px;
    border-radius: 999px;
    font-weight: 700;
}

.sources-table {
    border-radius: 8px;
    overflow: hidden;
}
</style>
