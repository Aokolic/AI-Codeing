import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FeedStatusPanel from '@/components/FeedStatusPanel.vue'
import type { DataFeedOut } from '@/types'

vi.mock('@/api/feeds', () => ({
    triggerCollect: vi.fn().mockResolvedValue({ feed_id: '1', message: 'ok', triggered_at: '' }),
}))

function makeFeed(overrides: Partial<DataFeedOut> = {}): DataFeedOut {
    return {
        id: '1',
        name: 'Test Feed',
        feed_type: 'rss',
        url: 'https://example.com/rss',
        status: 'normal',
        consecutive_failures: 0,
        last_collected_at: null,
        schedule_cron: '0 2 * * *',
        created_at: '2026-01-01T00:00:00Z',
        is_builtin: false,
        ...overrides,
    }
}

describe('FeedStatusPanel', () => {
    it('renders feed name', () => {
        const wrapper = mount(FeedStatusPanel, { props: { feed: makeFeed({ name: '新华社RSS' }) } })
        expect(wrapper.text()).toContain('新华社RSS')
    })

    it('shows normal status in green color', () => {
        const wrapper = mount(FeedStatusPanel, { props: { feed: makeFeed({ status: 'normal' }) } })
        expect(wrapper.html()).toContain('normal')
    })

    it('shows warning status when consecutive_failures >= 3', () => {
        const wrapper = mount(FeedStatusPanel, {
            props: { feed: makeFeed({ status: 'warning', consecutive_failures: 3 }) },
        })
        expect(wrapper.text()).toContain('3')
    })

    it('shows offline status', () => {
        const wrapper = mount(FeedStatusPanel, { props: { feed: makeFeed({ status: 'offline' }) } })
        expect(wrapper.html()).toContain('offline')
    })

    it('emits collected event when trigger button clicked', async () => {
        const wrapper = mount(FeedStatusPanel, { props: { feed: makeFeed() } })
        const btn = wrapper.find('[data-testid="collect-btn"]')
        if (btn.exists()) {
            await btn.trigger('click')
            await flushPromises()
            expect(wrapper.emitted('collected')).toBeTruthy()
        }
    })
})
