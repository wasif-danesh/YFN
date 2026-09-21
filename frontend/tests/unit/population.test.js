import { expect, it } from 'vitest'
import { populationPlot } from '../../app/utils/population.js'
it('uses actual years, orders records and calculates endpoint change', () => {
  const plot = populationPlot([
    { year: 2025, population: 25267 },
    { year: 2020, population: 20865 },
  ])
  expect(plot.change).toBe(4402)
  expect(plot.rows.map((row) => row.year)).toEqual([
    2020, 2021, 2022, 2023, 2024, 2025,
  ])
  expect(plot.segments).toHaveLength(2)
  expect(plot.points[1].y).toBeNull()
  expect(plot.ticks[0].value).toBe(0)
})
it('does not bridge null years or invent missing endpoint totals', () => {
  const plot = populationPlot([
    { year: 2020, population: null },
    { year: 2021, population: 30 },
    { year: 2022, population: null },
    { year: 2023, population: 40 },
  ])
  expect(plot.change).toBeNull()
  expect(plot.segments.map((segment) => segment.length)).toEqual([1, 1])
})
it('handles empty, single-year and zero series without invalid chart coordinates', () => {
  expect(populationPlot([]).rows).toEqual([])
  expect(populationPlot([{ year: 2020, population: 0 }]).change).toBeNull()
  const plot = populationPlot([
    { year: 2020, population: 0 },
    { year: 2021, population: 0 },
  ])
  expect(plot.change).toBe(0)
  expect(plot.points.every((point) => Number.isFinite(point.y))).toBe(true)
})
