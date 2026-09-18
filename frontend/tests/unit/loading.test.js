import { afterEach, beforeEach, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingStatus from '../../app/components/LoadingStatus.vue'
import AreaSearch from '../../app/components/AreaSearch.vue'
let wrapper
beforeEach(() => vi.useFakeTimers())
afterEach(() => {
  wrapper?.unmount()
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

it('explains longer waits in stages without a countdown', async () => {
  wrapper = mount(LoadingStatus, {
    props: { label: 'Loading your areas…', hint: 'You can explore the map.' },
  })
  expect(wrapper.attributes('role')).toBe('status')
  expect(wrapper.get('.loading-spinner').attributes('aria-hidden')).toBe('true')
  expect(wrapper.text()).toBe('Loading your areas…')
  await vi.advanceTimersByTimeAsync(5000)
  expect(wrapper.text()).toContain('Starting the area service…')
  expect(wrapper.text()).toContain('The first visit can take up to a minute.')
  expect(wrapper.text()).toContain('You can explore the map.')
  await vi.advanceTimersByTimeAsync(25000)
  expect(wrapper.text()).toContain('Almost there…')
  expect(wrapper.text()).toContain('no need to refresh')
  expect(wrapper.text()).not.toMatch(/\d+\s*(%|seconds)/)
})

it('clears its timers when loading finishes', () => {
  wrapper = mount(LoadingStatus)
  wrapper.unmount()
  wrapper = null
  expect(vi.getTimerCount()).toBe(0)
})

it('shows the staged loading status while area search waits for the service', async () => {
  vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
  wrapper = mount(AreaSearch, {
    props: {
      apiBase: 'https://api.example/api/v1',
      loadingHint: 'You can explore the map in the meantime.',
    },
    global: { stubs: { SiteIcon: true } },
  })
  await wrapper.get('input').setValue('carl')
  await vi.advanceTimersByTimeAsync(250)
  expect(wrapper.get('.loading-status').text()).toBe('Loading areas…')
  await vi.advanceTimersByTimeAsync(5000)
  expect(wrapper.get('.loading-status').text()).toContain(
    'You can explore the map in the meantime.',
  )
  expect(wrapper.get('input').element.value).toBe('carl')
})
