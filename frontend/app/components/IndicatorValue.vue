<script setup>
import { formatIndicator, displayUnit } from '../utils/areas.js'
defineProps({ indicator: { type: Object, default: null } })
function coverage(value) {
  return new Intl.NumberFormat('en-AU', {
    style: 'percent',
    maximumFractionDigits: 1,
  }).format(value)
}
</script>
<template>
  <div class="indicator-value">
    <template v-if="indicator">
      <strong class="measure-value">{{ formatIndicator(indicator) }}</strong>
      <span v-if="indicator.raw_value !== null" class="measure-unit">{{
        displayUnit(indicator.unit)
      }}</span>
      <p class="measure-period">{{ indicator.reference_period }}</p>
      <span v-if="indicator.quality.status === 'limited'" class="quality-label"
        >Provisional</span
      >
      <p v-if="indicator.raw_value === null" class="missing-note">
        {{
          indicator.quality.reason ||
          'This measure is not available for this area.'
        }}
      </p>
      <details class="measure-details">
        <summary>Source &amp; coverage notes</summary>
        <p>{{ indicator.explanation }}</p>
        <p v-if="indicator.raw_value !== null">
          {{ indicator.quality.reason }}
        </p>
        <p v-if="indicator.quality.coverage_fraction != null">
          Area coverage: {{ coverage(indicator.quality.coverage_fraction) }}.
          This describes covered land, not the share of residents with access.
        </p>
        <ul>
          <li v-for="source in indicator.sources" :key="source.source_id">
            <a
              :href="/^https?:\/\//.test(source.url) ? source.url : undefined"
              target="_blank"
              rel="noopener noreferrer"
              >{{ source.dataset_name }}</a
            ><span
              >{{ source.publisher }} · {{ source.reference_period }} ·
              {{ source.licence }}</span
            >
            <p>{{ source.limitation }}</p>
          </li>
        </ul>
      </details>
    </template>
    <template v-else
      ><strong class="measure-value">Not available</strong>
      <p class="missing-note">
        No observation is available for this measure.
      </p></template
    >
  </div>
</template>
