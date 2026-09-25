<script setup>
import {
  comparisonMeasures,
  getIndicator,
  comparisonNote,
  barRatio,
} from '../utils/comparison.js'
defineProps({ entries: { type: Array, required: true } })
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
              :ratio="barRatio(entries, row.key, entry.area.sa2_code)"
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
