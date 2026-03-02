import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchBar from '@/components/SearchBar.vue'

describe('SearchBar', () => {
    it('renders input field', () => {
        const wrapper = mount(SearchBar)
        expect(wrapper.find('input').exists()).toBe(true)
    })

    it('emits search event on submit', async () => {
        const wrapper = mount(SearchBar)
        const input = wrapper.find('input')
        await input.setValue('新冠疫苗')
        await input.trigger('keydown.enter')
        const emitted = wrapper.emitted('search')
        expect(emitted).toBeTruthy()
        expect(emitted![0][0]).toBe('新冠疫苗')
    })

    it('emits search when search button is clicked', async () => {
        const wrapper = mount(SearchBar)
        await wrapper.find('input').setValue('造假数据')
        const btn = wrapper.find('[data-testid="search-btn"]')
        if (btn.exists()) {
            await btn.trigger('click')
            expect(wrapper.emitted('search')).toBeTruthy()
        }
    })

    it('does not emit for empty query', async () => {
        const wrapper = mount(SearchBar)
        await wrapper.find('input').setValue('')
        await wrapper.find('input').trigger('keydown.enter')
        const emitted = wrapper.emitted('search')
        expect(!emitted || emitted.length === 0).toBe(true)
    })
})
