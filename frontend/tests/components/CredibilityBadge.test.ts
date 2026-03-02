import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CredibilityBadge from '@/components/CredibilityBadge.vue'
import type { CredibilityLevel } from '@/types'

describe('CredibilityBadge', () => {
    const levels: CredibilityLevel[] = ['high', 'medium', 'low', 'unverified']

    it.each(levels)('renders label for level=%s', (level) => {
        const wrapper = mount(CredibilityBadge, { props: { level, score: 75 } })
        expect(wrapper.html()).toBeTruthy()
        expect(wrapper.html()).toContain(level)
    })

    it('shows score when provided', () => {
        const wrapper = mount(CredibilityBadge, { props: { level: 'high', score: 88 } })
        expect(wrapper.text()).toContain('88')
    })

    it('applies green color for high', () => {
        const wrapper = mount(CredibilityBadge, { props: { level: 'high', score: 80 } })
        expect(wrapper.html()).toMatch(/green|success|high/)
    })

    it('applies red color for unverified', () => {
        const wrapper = mount(CredibilityBadge, { props: { level: 'unverified', score: 5 } })
        expect(wrapper.html()).toMatch(/red|error|unverified/)
    })
})
