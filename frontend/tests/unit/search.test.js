import { afterEach, beforeEach, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AreaSearch from '../../app/components/AreaSearch.vue'
const carlton = { sa2_code: '206041117', name: 'Carlton', is_comparable: true }
const result = (areas) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ areas }),
})
let wrapper
beforeEach(() => vi.useFakeTimers())
afterEach(() => {
  wrapper?.unmount()
  vi.unstubAllGlobals()
  vi.useRealTimers()
})
function mountSearch(props = {}) {
  wrapper = mount(AreaSearch, {
    props: { apiBase: 'https://api.example/api/v1', ...props },
    global: { stubs: { SiteIcon: true } },
  })
  return wrapper
}
it('supports keyboard choice, Escape, and excludes selected areas', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockResolvedValue(
        result([
          carlton,
          { ...carlton, sa2_code: '206071140', name: 'Carlton North' },
        ]),
      ),
  )
  mountSearch({ excluded: ['206071140'] })
  const input = wrapper.get('input')
  await input.setValue('carl')
  await vi.advanceTimersByTimeAsync(250)
  await flushPromises()
  expect(wrapper.findAll('[role="option"]')).toHaveLength(1)
  await input.trigger('keydown', { key: 'ArrowDown' })
  await input.trigger('keydown', { key: 'Enter' })
  expect(wrapper.emitted('select')[0][0]).toEqual(carlton)
  expect(input.attributes('aria-expanded')).toBe('false')
  await input.trigger('focus')
  await input.trigger('keydown', { key: 'Escape' })
  expect(input.attributes('aria-expanded')).toBe('false')
})
it('discards slower responses for an earlier query', async () => {
  let resolveOld
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveOld = resolve
          }),
      )
      .mockResolvedValue(result([carlton])),
  )
  mountSearch()
  const input = wrapper.get('input')
  await input.setValue('foot')
  await vi.advanceTimersByTimeAsync(250)
  await input.setValue('carl')
  await vi.advanceTimersByTimeAsync(250)
  await flushPromises()
  resolveOld(result([{ ...carlton, name: 'Footscray' }]))
  await flushPromises()
  expect(wrapper.text()).toContain('Carlton')
  expect(wrapper.text()).not.toContain('Footscray')
})
it('shows an error, supports retry, and handles no matches', async () => {
  const fetcher = vi.fn().mockRejectedValue(new TypeError('offline'))
  vi.stubGlobal('fetch', fetcher)
  mountSearch()
  await wrapper.get('input').setValue('none')
  await vi.advanceTimersByTimeAsync(250)
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toContain('couldn’t load')
  fetcher.mockResolvedValue(result([]))
  await wrapper.get('button').trigger('click')
  await flushPromises()
  expect(wrapper.text()).toContain('No matching areas')
})
