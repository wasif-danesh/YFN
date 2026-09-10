<script setup>
import { computed } from 'vue'
import { populationPlot } from '../utils/population.js'
const props = defineProps({
  history: { type: Array, required: true },
  sources: { type: Array, default: () => [] },
})
const plot = computed(() => populationPlot(props.history))
const number = (value) => new Intl.NumberFormat('en-AU').format(value)
</script>
<template>
  <section class="population-section" aria-labelledby="population-title">
    <h2 id="population-title">Population history</h2>
    <div v-if="!plot.rows.length" class="comparison-feedback">
      Population history is not available for this area.
    </div>
    <div v-else class="population-panel">
      <div class="population-chart-column">
        <h3>Estimated residents, {{ plot.start }}–{{ plot.end }}</h3>
        <p class="chart-description">
          Historical population estimates. Missing years are shown as gaps.
        </p>
        <svg
          class="population-chart"
          viewBox="0 0 700 260"
          role="img"
          aria-labelledby="population-chart-title population-chart-description"
        >
          <title id="population-chart-title">
            Annual estimated resident population
          </title>
          <desc id="population-chart-description">
            Values and revision status for every year are provided in the table
            below. The vertical axis starts at zero.
          </desc>
          <g v-for="tick in plot.ticks" :key="tick.value">
            <line x1="64" x2="676" :y1="tick.y" :y2="tick.y" stroke="#dce7f5" />
            <text x="54" :y="tick.y + 4" text-anchor="end">
              {{ number(tick.value) }}
            </text>
          </g>
          <polyline
            v-for="(segment, index) in plot.segments"
            :key="index"
            :points="segment.map((point) => `${point.x},${point.y}`).join(' ')"
            fill="none"
            stroke="#1264de"
            stroke-width="3"
          />
          <g v-for="point in plot.points" :key="point.year">
            <text :x="point.x" y="244" text-anchor="middle">
              {{ point.year }}
            </text>
            <circle
              v-if="point.y !== null"
              :cx="point.x"
              :cy="point.y"
              r="4.5"
              fill="#1264de"
              stroke="white"
              stroke-width="1.5"
            >
              <title>
                {{ point.year }}: {{ number(point.population) }} residents ({{
                  point.revision_status
                }})
              </title>
            </circle>
          </g>
        </svg>
        <div
          class="population-table-wrap"
          tabindex="0"
          role="region"
          aria-label="Population history values"
        >
          <table class="population-table">
            <caption class="sr-only">
              Population estimates and revision status
            </caption>
            <thead>
              <tr>
                <th scope="col">Year</th>
                <th scope="col">Residents</th>
                <th scope="col">Reference date</th>
                <th scope="col">Estimate status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in plot.rows" :key="row.year">
                <th scope="row">{{ row.year }}</th>
                <td>
                  {{
                    row.population == null
                      ? 'Not available'
                      : number(row.population)
                  }}
                </td>
                <td>{{ row.reference_date || 'Not available' }}</td>
                <td>{{ row.revision_status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <aside class="population-summary">
        <h3>{{ plot.start }}–{{ plot.end }}</h3>
        <template v-if="plot.change !== null"
          ><strong>{{ number(Math.abs(plot.change)) }}</strong>
          <p>
            {{
              plot.change > 0
                ? 'more residents'
                : plot.change < 0
                  ? 'fewer residents'
                  : 'change in residents'
            }}
          </p>
          <p>
            Difference between the first and last year shown. These estimates
            describe the past, not a forecast.
          </p></template
        >
        <p v-else>
          A total change is not available because the endpoint estimates are
          missing or fewer than two years are available.
        </p>
        <div
          v-for="source in sources"
          :key="source.source_id"
          class="population-source"
        >
          <a
            :href="/^https?:\/\//.test(source.url) ? source.url : undefined"
            target="_blank"
            rel="noopener noreferrer"
            >{{ source.dataset_name }}</a
          >
          <p>{{ source.publisher }} · {{ source.licence }}</p>
          <p>{{ source.limitation }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>
