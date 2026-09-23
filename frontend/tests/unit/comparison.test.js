import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import realResponse from '../../../contracts/examples/compare.json'
import { rentDifference, detailsLocation } from '../../app/utils/comparison.js'
import IndicatorValue from '../../app/components/IndicatorValue.vue'
const real = realResponse.areas
const clone = () => structuredClone(real)
describe('historical rent difference', () => {
  it('uses real matching Census medians without ranking the areas', () => {
    expect(rentDifference(real)).toBe(
      'Carlton’s median weekly reported rent was $10 higher than Footscray’s in the 2021 Census.',
    )
  })
  it('handles ties and three-area ranges', () => {
    const entries = clone()
    entries[1].indicators[0].raw_value = 365
    expect(rentDifference(entries)).toContain('same median')
    entries.push(structuredClone(entries[0]))
    entries[2].indicators[0].raw_value = 400
    expect(rentDifference(entries)).toContain('ranged from $365 to $400')
  })
  it('withholds differences for one area, missing, limited or mismatched data', () => {
    expect(rentDifference(real.slice(0, 1))).toBeNull()
    for (const patch of [
      { raw_value: null },
      { reference_period: '2022' },
      { method_version: 'different' },
      { unit: 'other' },
      { quality: { status: 'limited' } },
    ]) {
      const entries = clone()
      Object.assign(entries[0].indicators[0], patch)
      expect(rentDifference(entries)).toBeNull()
    }
  })
})
it('preserves comparison order in the details link', () => {
  expect(detailsLocation('213031348', ['206041117', '213031348'])).toEqual({
    path: '/areas/213031348',
    query: { compare: '206041117,213031348' },
  })
})
it('shows nulls, zero and source/coverage limitations explicitly', () => {
  const indicator = structuredClone(real[0].indicators[1])
  indicator.raw_value = null
  indicator.quality.reason = 'Missing observation'
  let wrapper = mount(IndicatorValue, { props: { indicator } })
  expect(wrapper.text()).toContain('Not available')
  expect(wrapper.text()).toContain('Missing observation')
  wrapper.unmount()
  indicator.raw_value = 0
  indicator.quality.coverage_fraction = 0.125
  wrapper = mount(IndicatorValue, { props: { indicator } })
  expect(wrapper.get('.measure-value').text()).toBe('0')
  expect(wrapper.text()).toContain('12.5%')
  expect(wrapper.findAll('a').length).toBeGreaterThan(0)
  wrapper.unmount()
})
