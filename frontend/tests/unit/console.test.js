import { afterEach, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ApiConsole from '../../app/components/ApiConsole.vue'

afterEach(() => vi.unstubAllGlobals())
const success = () => ({ status: 200, ok: true, text: async () => JSON.stringify({ raw_value: null, publication_ready: false }) })

it('automatically calls all four endpoints and displays exact JSON including null', async () => {
  const fetcher = vi.fn().mockImplementation(async () => success())
  vi.stubGlobal('fetch', fetcher)
  const wrapper = mount(ApiConsole, { props: { apiBase: 'https://api.example/api/v1' } })
  await flushPromises()
  expect(fetcher).toHaveBeenCalledTimes(4)
  expect(wrapper.findAll('pre')).toHaveLength(4)
  expect(wrapper.text()).toContain('4 of 4 requests successful')
  expect(wrapper.find('pre').text()).toContain('"raw_value": null')
  expect(wrapper.text()).toContain('not the renter homepage')
  wrapper.unmount()
})

it('shows connection errors independently and allows individual retry', async () => {
  const fetcher = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
  vi.stubGlobal('fetch', fetcher)
  const wrapper = mount(ApiConsole, { props: { apiBase: 'https://api.example/api/v1' } })
  await flushPromises()
  expect(wrapper.findAll('[role="alert"]')).toHaveLength(4)
  fetcher.mockImplementation(async () => success())
  await wrapper.get('button[aria-label="Run Service health"]').trigger('click')
  await flushPromises()
  expect(wrapper.text()).toContain('1 of 4 requests successful')
  expect(wrapper.findAll('[role="alert"]')).toHaveLength(3)
  wrapper.unmount()
})

it('shows loading while requests are pending and displays HTTP error JSON', async () => {
  let finish
  const pending = new Promise(resolve => { finish = resolve })
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(pending))
  const wrapper = mount(ApiConsole, { props: { apiBase: 'https://api.example/api/v1' } })
  await flushPromises()
  expect(wrapper.get('.primary-button').attributes()).toHaveProperty('disabled')
  expect(wrapper.text()).toContain('Waiting for the API')
  finish({ status: 503, ok: false, text: async () => '{"error":{"code":"DATABASE_UNAVAILABLE"}}' })
  await flushPromises()
  expect(wrapper.text()).toContain('HTTP 503')
  expect(wrapper.text()).toContain('DATABASE_UNAVAILABLE')
  wrapper.unmount()
})
