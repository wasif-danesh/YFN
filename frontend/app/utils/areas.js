export function selectionCodes(value) {
  if (value == null || value === '') return []
  if (typeof value !== 'string')
    throw new Error('Choose up to three different areas.')
  const codes = value.split(',')
  if (
    codes.length > 3 ||
    new Set(codes).size !== codes.length ||
    codes.some((code) => !/^\d{9}$/.test(code))
  )
    throw new Error('Choose up to three different areas using the area search.')
  return codes
}
export function formatIndicator(indicator) {
  if (indicator.raw_value == null) return 'Not available'
  const value = indicator.raw_value
  if (indicator.unit === 'AUD/week')
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      maximumFractionDigits: 0,
    }).format(value)
  const number = new Intl.NumberFormat('en-AU', {
    maximumFractionDigits: 1,
  }).format(value)
  if (indicator.unit === 'percent' || indicator.unit === '%')
    return `${number}%`
  return number
}
export function displayUnit(unit) {
  return (
    {
      'AUD/week': 'per week',
      access_index: 'access index',
      'sqm/person': 'm² per resident',
      'm2/person': 'm² per resident',
      percent: 'population change',
      '%': 'population change',
    }[unit] || unit
  )
}
