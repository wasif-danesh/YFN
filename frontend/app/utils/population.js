// Chart data is derived only from the returned observations. Gaps stay gaps.
export function populationPlot(history) {
  const sorted = [...history].sort((a, b) => a.year - b.year)
  if (!sorted.length)
    return { rows: [], points: [], segments: [], ticks: [], change: null }
  const byYear = new Map(sorted.map((row) => [row.year, row]))
  const start = sorted[0].year,
    end = sorted.at(-1).year
  const rows = Array.from(
    { length: end - start + 1 },
    (_, index) =>
      byYear.get(start + index) || {
        year: start + index,
        population: null,
        revision_status: 'unavailable',
        reference_date: null,
      },
  )
  const maximum = Math.max(
    0,
    ...rows
      .filter((row) => row.population != null)
      .map((row) => row.population),
  )
  const roughStep = maximum / 4 || 1
  const magnitude = 10 ** Math.floor(Math.log10(roughStep))
  const step = Math.ceil(roughStep / magnitude) * magnitude
  const ceiling = step * 4
  const x = (index) =>
    rows.length === 1 ? 362 : 64 + (index * 612) / (rows.length - 1)
  const y = (value) => 216 - (value / ceiling) * 192
  const points = rows.map((row, index) => ({
    ...row,
    x: x(index),
    y: row.population == null ? null : y(row.population),
  }))
  const segments = []
  let segment = []
  for (const point of points) {
    if (point.y === null) {
      if (segment.length) segments.push(segment)
      segment = []
    } else segment.push(point)
  }
  if (segment.length) segments.push(segment)
  const first = rows[0],
    last = rows.at(-1)
  const change =
    rows.length > 1 && first.population != null && last.population != null
      ? last.population - first.population
      : null
  return {
    rows,
    points,
    segments,
    ticks: Array.from({ length: 5 }, (_, index) => ({
      value: step * index,
      y: y(step * index),
    })),
    change,
    start,
    end,
  }
}
