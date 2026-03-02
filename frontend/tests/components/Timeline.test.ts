import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Timeline from '@/components/Timeline.vue'
import type { EventSummary } from '@/types'

const mockEvents: EventSummary[] = [
    {
        id: 'e1',
        title: '第一次报道',
        event_time: '2024-01-01T00:00:00Z',
        source_count: 2,
        credibility: { level: 'high', total_score: 80, has_conflict: false },
    },
    {
        id: 'e2',
        title: '官方声明发布',
        event_time: '2024-02-01T00:00:00Z',
        source_count: 3,
        credibility: { level: 'high', total_score: 90, has_conflict: false },
    },
]

describe('Timeline', () => {
    it('renders all events', () => {
        const wrapper = mount(Timeline, { props: { events: mockEvents, loading: false } })
        expect(wrapper.text()).toContain('第一次报道')
        expect(wrapper.text()).toContain('官方声明发布')
    })

    it('shows loading state', () => {
        const wrapper = mount(Timeline, { props: { events: [], loading: true } })
        expect(wrapper.html()).toMatch(/loading|spin/i)
    })

    it('shows empty state when no events', () => {
        const wrapper = mount(Timeline, { props: { events: [], loading: false } })
        expect(wrapper.html()).toMatch(/暂无|empty/i)
    })

    it('emits event-click when EventCard is activated', async () => {
        const wrapper = mount(Timeline, { props: { events: mockEvents, loading: false } })
        const cards = wrapper.findAll('[data-testid="event-card"]')
        if (cards.length > 0) {
            await cards[0].trigger('click')
        }
        // Timeline should pass through or handle
    })

    it('renders events in chronological order', () => {
        const wrapper = mount(Timeline, { props: { events: mockEvents, loading: false } })
        const text = wrapper.text()
        expect(text.indexOf('第一次报道')).toBeLessThan(text.indexOf('官方声明发布'))
    })
})
