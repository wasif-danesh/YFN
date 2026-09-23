<script setup>
import {
  comparisonMeasures,
  getIndicator,
  comparisonNote,
} from '../utils/comparison.js'
const props = defineProps({ entries: { type: Array, required: true } })
// Values available for a measure across the areas being compared, so a bar
// only appears when there is something to compare (2+ available values) —
// never for a single area, and never implying a rating on its own.
function ratiosFor(key) {
  const values = props.entries
    .map((entry) => getIndicator(entry, key))
    .filter((indicator) => indicator && indicator.raw_value !== null)
    .map((indicator) => indicator.raw_value)
  const max = values.length >= 2 ? Math.max(...values) : null
  return max > 0 ? max : null
}
function ratioFor(entry, key, max) {
  if (max === null) return null
  const indicator = getIndicator(entry, key)
  if (!indicator || indicator.raw_value === null) return null
  return indicator.raw_value / max
}
</script>
<template>
  <p id="comparison-scroll-hint" class="comparison-scroll-hint">
    On smaller screens, swipe the table to see each area and the explanations.
  </p>
  <div
    class="comparison-table-wrap completed-table"
    role="region"
    tabindex="0"
    aria-label="Area comparison"
    aria-describedby="comparison-scroll-hint"
  >
    <table
      class="comparison-table"
      :class="{ 'three-areas': entries.length === 3 }"
    >
      <caption class="sr-only">
        The same four measures for
        {{
          entries.map((entry) => entry.area.name).join(', ')
        }}, with source dates and limitations.
      </caption>
      <thead>
        <tr>
          <th scope="col" class="measure-column">Measure</th>
          <th v-for="entry in entries" :key="entry.area.sa2_code" scope="col">
            {{ entry.area.name }}<span>SA2 area</span>
          </th>
          <th scope="col" class="meaning-column">What it means</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in comparisonMeasures"
          :key="row.key"
          :data-measure="row.key"
        >
          <th scope="row" class="measure-column">
            <span class="measure-heading"
              ><span class="category-icon"><SiteIcon :name="row.icon" /></span
              >{{ row.title }}</span
            >
            <p class="row-subtitle">{{ row.subtitle }}</p>
          </th>
          <td
            v-for="entry in entries"
            :key="entry.area.sa2_code"
            :data-area="entry.area.sa2_code"
          >
            <IndicatorValue
              :indicator="getIndicator(entry, row.key)"
              :ratio="ratioFor(entry, row.key, ratiosFor(row.key))"
              :note="
                row.showComparisonNote
                  ? comparisonNote(entries, row.key, entry.area.sa2_code)
                  : null
              "
            />
          </td>
          <td class="meaning-column">
            <p>{{ row.meaning }}</p>
          </td>
        </tr>
      </tbody>
    </table>
    <p class="table-footnote">
      SA2 statistical areas may cover part of a suburb or several suburbs. The
      boundaries used here are from 2021.
    </p>
  </div>
</template>
