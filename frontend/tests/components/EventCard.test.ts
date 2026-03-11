import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EventCard from '@/components/EventCard.vue'
import type { EventSummary } from '@/types'

const mockEvent: EventSummary = {
    id: 'e1',
    title: '初步报道：疫苗副作用争议',
    event_time: '2024-06-01T10:00:00Z',
    source_count: 3,
    credibility: { level: 'high', total_score: 82.5, has_conflict: false },
    sources: [
        { id: 's1', name: '新华社', source_type: 'government' },
        { id: 's2', name: '央视网', source_type: 'mainstream_media' },
    ],
}

describe('EventCard', () => {
    it('renders event title', () => {
        const wrapper = mount(EventCard, { props: { event: mockEvent } })
        expect(wrapper.text()).toContain('初步报道：疫苗副作用争议')
    })

    it('displays source count', () => {
        const wrapper = mount(EventCard, { props: { event: mockEvent } })
        expect(wrapper.text()).toContain('3')
    })

    it('shows credibility indicator', () => {
        const wrapper = mount(EventCard, { props: { event: mockEvent } })
        // CredibilityBadge should be rendered with high level
        expect(wrapper.html()).toContain('high')
    })

    it('expands on click to show details', async () => {
        const wrapper = mount(EventCard, { props: { event: mockEvent } })
        await wrapper.trigger('click')
        expect(wrapper.emitted('expand')).toBeTruthy()
    })

    it('shows conflict warning when has_conflict is true', () => {
        const conflictEvent = { ...mockEvent, credibility: { level: 'medium' as const, total_score: 55, has_conflict: true } }
        const wrapper = mount(EventCard, { props: { event: conflictEvent } })
        expect(wrapper.html()).toContain('credibility-warning')
    })

    it('applies low-credibility warning class for unverified events', () => {
        const unverified = { ...mockEvent, credibility: { level: 'unverified' as const, total_score: 10, has_conflict: false } }
        const wrapper = mount(EventCard, { props: { event: unverified } })
        expect(wrapper.html()).toMatch(/unverified|low-credibility/)
    })
})
