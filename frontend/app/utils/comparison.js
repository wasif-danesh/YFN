export const comparisonMeasures = [
  {
    key: 'rent_weekly',
    title: 'Median weekly rent',
    icon: 'home',
    subtitle: '2021 Census reported rent',
    meaning:
      'Reported rent in 2021, not current advertised rent. Compare current listings before deciding on a budget.',
  },
  {
    key: 'transport_access',
    title: 'Public transport',
    icon: 'train',
    subtitle: 'Raw access index',
    meaning:
      'An area-level morning access measure over covered land. A higher value means more access, not necessarily a better area. It is not a commute time, and coverage varies between areas.',
    showComparisonNote: true,
  },
  {
    key: 'population_growth',
    title: 'Population change',
    icon: 'people',
    subtitle: 'Historical change, not a forecast',
    meaning:
      'Change in estimated resident population over the dates shown. Faster growth can mean more competition for housing and demand on local services; slower or falling numbers can mean less pressure. Estimates can be revised, and growth alone does not predict rent or service availability.',
  },
  {
    key: 'green_space_per_resident',
    title: 'Open space per resident',
    icon: 'leaf',
    subtitle: 'Selected open space',
    meaning:
      'Selected public open-space records divided by population. A higher value means more open space per person, not necessarily higher quality or walking access.',
    showComparisonNote: true,
  },
]

export function getIndicator(entry, key) {
  return entry.indicators.find((indicator) => indicator.key === key)
}

// A plain-language read of a raw, unfamiliar number (e.g. a transport access
// index) relative to the other areas in this comparison — never a rating or
// a claim against an outside benchmark, only "higher/lower than what you're
// looking at right now".
export function comparisonNote(entries, key, code) {
  const values = entries
    .map((entry) => ({
      code: entry.area.sa2_code,
      name: entry.area.name,
      value: getIndicator(entry, key)?.raw_value,
    }))
    .filter((v) => v.value !== null && v.value !== undefined)
  if (values.length < 2) return null
  const current = values.find((v) => v.code === code)
  if (!current) return null
  if (values.length === 2) {
    const other = values.find((v) => v.code !== code)
    if (current.value === other.value) return `Same as ${other.name}`
    return current.value > other.value
      ? `Higher than ${other.name}`
      : `Lower than ${other.name}`
  }
  const sorted = [...values].sort((a, b) => b.value - a.value)
  if (sorted[0].value === sorted.at(-1).value) return null
  if (sorted[0].code === code && sorted[0].value > sorted[1].value)
    return 'The highest of your selected areas'
  if (sorted.at(-1).code === code && sorted.at(-1).value < sorted.at(-2).value)
    return 'The lowest of your selected areas'
  return 'Between the areas you selected'
}

// A descriptive difference in matching historical measures, never a saving or ranking.
export function rentDifference(entries) {
  if (entries.length < 2) return null
  const rents = entries.map((entry) => ({
    name: entry.area.name,
    measure: getIndicator(entry, 'rent_weekly'),
  }))
  if (
    rents.some(
      ({ measure }) =>
        !measure ||
        measure.raw_value == null ||
        measure.quality.status !== 'available',
    )
  )
    return null
  const first = rents[0].measure
  if (
    rents.some(
      ({ measure }) =>
        measure.unit !== 'AUD/week' ||
        measure.reference_period !== first.reference_period ||
        measure.method_version !== first.method_version,
    )
  )
    return null
  const ordered = [...rents].sort(
    (a, b) => a.measure.raw_value - b.measure.raw_value,
  )
  const low = ordered[0],
    high = ordered.at(-1)
  const money = (value) =>
    new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      maximumFractionDigits: 0,
    }).format(value)
  if (low.measure.raw_value === high.measure.raw_value)
    return `The selected areas had the same median weekly reported rent of ${money(low.measure.raw_value)} in the ${first.reference_period}.`
  if (entries.length === 2)
    return `${high.name}’s median weekly reported rent was ${money(high.measure.raw_value - low.measure.raw_value)} higher than ${low.name}’s in the ${first.reference_period}.`
  return `Median weekly reported rent ranged from ${money(low.measure.raw_value)} to ${money(high.measure.raw_value)} across your selected areas in the ${first.reference_period} — a difference of ${money(high.measure.raw_value - low.measure.raw_value)}.`
}

export function detailsLocation(code, selectedCodes) {
  return { path: `/areas/${code}`, query: { compare: selectedCodes.join(',') } }
}
