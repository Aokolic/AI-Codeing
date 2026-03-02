import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CredibilityPanel from '@/components/CredibilityPanel.vue'
import type { CredibilityDetail } from '@/types'

const mockDetail: CredibilityDetail = {
    event_id: 'e1',
    event_title: '测试事件',
    level: 'medium',
    total_score: 62.5,
    authority_score: 70,
    timeliness_score: 50,
    cross_verify_score: 65,
    source_count: 2,
    has_conflict: false,
    conflict_sources: [],
    sources: [],
    scoring_explanation: {
        authority: '两个来源权威性评分均值70',
        timeliness: '距今48小时，时效性50',
        cross_verify: '两个独立来源交叉验证，得分65',
    },
    assessed_at: '2026-01-01T00:00:00Z',
}

describe('CredibilityPanel', () => {
    it('renders total score', () => {
        const wrapper = mount(CredibilityPanel, { props: { detail: mockDetail } })
        // NStatistic may format 62.5 as "63" or "62.5" — just check the integer part
        expect(wrapper.text()).toMatch(/6[23]/)
    })

    it('renders three dimension scores', () => {
        const wrapper = mount(CredibilityPanel, { props: { detail: mockDetail } })
        expect(wrapper.text()).toContain('70')
        expect(wrapper.text()).toContain('50')
        expect(wrapper.text()).toContain('65')
    })

    it('shows conflict warning when has_conflict is true', () => {
        const conflict = { ...mockDetail, has_conflict: true, conflict_sources: ['新华社', '人民日报'] }
        const wrapper = mount(CredibilityPanel, { props: { detail: conflict } })
        expect(wrapper.text()).toMatch(/来源分歧|conflict/)
    })

    it('shows scoring explanation text', () => {
        const wrapper = mount(CredibilityPanel, { props: { detail: mockDetail } })
        expect(wrapper.text()).toContain('权威')
    })
})
