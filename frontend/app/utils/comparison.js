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
      'An area-level morning access measure over covered land. It is not a commute time. The method and source date remain unconfirmed.',
  },
  {
    key: 'population_growth',
    title: 'Population change',
    icon: 'people',
    subtitle: 'Historical change, not a forecast',
    meaning:
      'Change in estimated resident population over the dates shown. Estimates can be revised. Growth alone does not predict rent or service availability.',
  },
  {
    key: 'green_space_per_resident',
    title: 'Open space per resident',
    icon: 'leaf',
    subtitle: 'Selected open space',
    meaning:
      'Selected open space divided by population. The inventory date and completeness are unverified; this does not measure walking access or park quality.',
  },
]

export function getIndicator(entry, key) {
  return entry.indicators.find((indicator) => indicator.key === key)
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
