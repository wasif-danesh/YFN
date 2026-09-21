import { expect, it } from 'vitest'
import {
  selectionCodes,
  formatIndicator,
  displayUnit,
} from '../../app/utils/areas.js'

it('keeps string SA2 identities and rejects invalid, duplicate and excessive URL selections', () => {
  expect(selectionCodes(undefined)).toEqual([])
  expect(selectionCodes('206041117,213031348')).toEqual([
    '206041117',
    '213031348',
  ])
  for (const value of [
    '1',
    '206041117,206041117',
    '206041117, 213031348',
    ['206041117'],
    '206041117,213031348,212051567,212021454',
  ])
    expect(() => selectionCodes(value)).toThrow()
})
it('preserves missing values, zero and negative population change', () => {
  expect(formatIndicator({ raw_value: null, unit: 'AUD/week' })).toBe(
    'Not available',
  )
  expect(formatIndicator({ raw_value: 0, unit: 'percent' })).toBe('0%')
  expect(formatIndicator({ raw_value: -2.56, unit: 'percent' })).toBe('-2.6%')
  expect(formatIndicator({ raw_value: 365, unit: 'AUD/week' })).toBe('$365')
  expect(displayUnit('m2/person')).toBe('m² per resident')
})
