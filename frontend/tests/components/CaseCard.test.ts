import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { RouterLinkStub } from '@vue/test-utils'
import CaseCard from '@/components/CaseCard.vue'
import type { CaseSummary } from '@/types'

const mockCase: CaseSummary = {
    id: 'c1',
    title: '某省高考顶替事件',
    status: 'active',
    hotness_score: 87.5,
    tags: [{ id: 't1', name: '教育' }],
    event_count: 8,
    source_count: 12,
    created_at: '2024-01-01T00:00:00Z',
    last_event_at: '2024-06-01T00:00:00Z',
}

describe('CaseCard', () => {
    const globalStubs = { RouterLink: RouterLinkStub }

    it('renders case title', () => {
        const wrapper = mount(CaseCard, { props: { case: mockCase }, global: { stubs: globalStubs } })
        expect(wrapper.text()).toContain('某省高考顶替事件')
    })

    it('displays hotness score', () => {
        const wrapper = mount(CaseCard, { props: { case: mockCase }, global: { stubs: globalStubs } })
        // hotness_score 87.5 rounds to 87 or 88
        expect(wrapper.text()).toMatch(/8[78]/)
    })

    it('shows tag names', () => {
        const wrapper = mount(CaseCard, { props: { case: mockCase }, global: { stubs: globalStubs } })
        expect(wrapper.text()).toContain('教育')
    })

    it('shows event and source counts', () => {
        const wrapper = mount(CaseCard, { props: { case: mockCase }, global: { stubs: globalStubs } })
        expect(wrapper.text()).toContain('8')
        expect(wrapper.text()).toContain('12')
    })

    it('links to case detail page', () => {
        const wrapper = mount(CaseCard, { props: { case: mockCase }, global: { stubs: globalStubs } })
        const link = wrapper.findComponent(RouterLinkStub)
        expect(link.props().to).toContain('c1')
    })
})
