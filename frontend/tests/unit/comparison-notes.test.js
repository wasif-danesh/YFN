import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import realResponse from '../../../contracts/examples/compare.json'
import { comparisonNote, barRatio } from '../../app/utils/comparison.js'
import IndicatorValue from '../../app/components/IndicatorValue.vue'

const real = realResponse.areas
const [carlton, footscray] = real.map((entry) => entry.area.sa2_code)
const clone = () => structuredClone(real)
const setValue = (entry, key, value) => {
  entry.indicators.find((indicator) => indicator.key === key).raw_value = value
}

describe('plain-language comparison note', () => {
  it('says higher or lower than the other area for two areas', () => {
    expect(comparisonNote(real, 'transport_access', carlton)).toBe(
      'Higher than Footscray',
    )
    expect(comparisonNote(real, 'transport_access', footscray)).toBe(
      'Lower than Carlton',
    )
  })
  it('says same as when two values are equal', () => {
    const entries = clone()
    setValue(entries[1], 'transport_access', entries[0].indicators[1].raw_value)
    expect(comparisonNote(entries, 'transport_access', carlton)).toBe(
      'Same as Footscray',
    )
  })
  it('says highest, lowest or between for three areas', () => {
    const entries = clone()
    entries.push(structuredClone(entries[0]))
    entries[2].area = { ...entries[0].area, sa2_code: '000000001', name: 'Third' }
    setValue(entries[2], 'transport_access', 30)
    setValue(entries[0], 'transport_access', 41.8)
    setValue(entries[1], 'transport_access', 24.8)
    expect(comparisonNote(entries, 'transport_access', carlton)).toContain('highest')
    expect(comparisonNote(entries, 'transport_access', '000000001')).toContain('Between')
    expect(comparisonNote(entries, 'transport_access', footscray)).toContain('lowest')
  })
  it('gives no note for one area, a missing value or all-equal values', () => {
    expect(comparisonNote(real.slice(0, 1), 'transport_access', carlton)).toBeNull()
    const missing = clone()
    setValue(missing[1], 'transport_access', null)
    expect(comparisonNote(missing, 'transport_access', carlton)).toBeNull()
    const equal = clone()
    equal.push(structuredClone(equal[0]))
    equal[2].area = { ...equal[0].area, sa2_code: '000000001', name: 'Third' }
    for (const entry of equal) setValue(entry, 'transport_access', 10)
    expect(comparisonNote(equal, 'transport_access', carlton)).toBeNull()
  })
})

describe('measure bar and note rendering', () => {
  const indicator = real[0].indicators[1]
  it('draws a decorative bar scaled to the ratio, with the value kept in text', () => {
    const wrapper = mount(IndicatorValue, { props: { indicator, ratio: 0.5 } })
    const bar = wrapper.get('.measure-bar')
    expect(bar.attributes('aria-hidden')).toBe('true')
    expect(wrapper.get('.measure-bar-fill').attributes('style')).toContain('width: 50%')
    expect(wrapper.get('.measure-value').text()).not.toBe('')
  })
  it('draws no bar and no note without a comparison', () => {
    const wrapper = mount(IndicatorValue, { props: { indicator } })
    expect(wrapper.find('.measure-bar').exists()).toBe(false)
    expect(wrapper.find('.measure-note').exists()).toBe(false)
  })
  it('shows the note text when given one', () => {
    const wrapper = mount(IndicatorValue, {
      props: { indicator, note: 'Higher than Footscray' },
    })
    expect(wrapper.get('.measure-note').text()).toBe('Higher than Footscray')
  })
})

describe('comparison bar ratio', () => {
  it('scales each area to the highest value being compared', () => {
    expect(barRatio(real, 'transport_access', carlton)).toBe(1)
    expect(barRatio(real, 'transport_access', footscray)).toBeCloseTo(24.8 / 41.8, 2)
  })
  it('draws no bar for one area or a missing value', () => {
    expect(barRatio(real.slice(0, 1), 'transport_access', carlton)).toBeNull()
    const missing = clone()
    setValue(missing[1], 'transport_access', null)
    expect(barRatio(missing, 'transport_access', carlton)).toBeNull()
    expect(barRatio(missing, 'transport_access', footscray)).toBeNull()
  })
  it('draws no bars when any value is negative, so a decline is never shown as a full bar', () => {
    const entries = clone()
    setValue(entries[0], 'population_growth', 21.1)
    setValue(entries[1], 'population_growth', -17.6)
    expect(barRatio(entries, 'population_growth', carlton)).toBeNull()
    expect(barRatio(entries, 'population_growth', footscray)).toBeNull()
  })
})
