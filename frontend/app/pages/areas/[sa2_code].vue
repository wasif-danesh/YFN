<script setup>
import { endpointUrl, requestJson } from '~/utils/api.js'
import { selectionCodes } from '~/utils/areas.js'
import { comparisonMeasures, getIndicator } from '~/utils/comparison.js'
const route = useRoute(),
  config = useRuntimeConfig()
const data = ref(null),
  loading = ref(false),
  error = ref('')
let controller,
  revision = 0,
  disposed = false
const returnCodes = computed(() => {
  try {
    const codes = selectionCodes(route.query.compare)
    if (codes.length) return codes
  } catch {
    /* Invalid context is never used as a redirect URL. */
  }
  return data.value?.area.is_comparable ? [data.value.area.sa2_code] : []
})
const returnLocation = computed(() => ({
  path: '/compare',
  query: returnCodes.value.length ? { sa2: returnCodes.value.join(',') } : {},
}))
useSeoMeta({
  title: () =>
    `${data.value?.area.name || 'Area details'} | Your Friendly Neighbourhood`,
  description:
    'Explore dated rent, transport, population history and open-space measures for a Greater Melbourne area.',
})
async function load() {
  const current = ++revision
  controller?.abort()
  controller = new AbortController()
  data.value = null
  error.value = ''
  loading.value = true
  try {
    const code = route.params.sa2_code
    if (typeof code !== 'string' || !/^\d{9}$/.test(code))
      throw new Error(
        'This area link is invalid. Choose an area from Home or Compare.',
      )
    const response = await requestJson(
      endpointUrl(config.public.apiBase, 'details', { detailCode: code }),
      { signal: controller.signal },
    )
    if (disposed || revision !== current) return
    if (!response.ok)
      throw new Error(
        response.body?.error?.message ||
          'Area details are temporarily unavailable.',
      )
    data.value = response.body
  } catch (cause) {
    if (!disposed && revision === current)
      error.value =
        cause instanceof TypeError || cause.name === 'AbortError'
          ? 'We couldn’t reach the service. It may be waking up. Please try again.'
          : cause.message
  } finally {
    if (!disposed && revision === current) loading.value = false
  }
}
watch(() => route.params.sa2_code, load)
onMounted(load)
onBeforeUnmount(() => {
  disposed = true
  revision++
  controller?.abort()
})
</script>
<template>
  <div class="renter-site">
    <SiteHeader :compare-to="returnLocation" />
    <main id="main" class="home-main details-main">
      <NuxtLink :to="returnLocation" class="back-link"
        >← Back to comparison</NuxtLink
      >
      <LoadingStatus
        v-if="loading"
        class="comparison-feedback"
        label="Loading area details…"
      />
      <div v-else-if="error" class="comparison-feedback">
        <h1>Area details unavailable</h1>
        <p role="alert">{{ error }}</p>
        <button class="text-button" @click="load">Try again</button> ·
        <NuxtLink to="/">Choose another area</NuxtLink>
      </div>
      <template v-else-if="data">
        <section class="home-intro">
          <div class="area-title">
            <h1>{{ data.area.name }}</h1>
            <span class="test-label">SA2 area</span>
          </div>
          <p>
            A closer look at rent, transport, population change and open space.
          </p>
          <p class="area-metadata">
            Greater Melbourne · ABS {{ data.area.boundary_year }} boundaries ·
            SA2 {{ data.area.sa2_code }}
          </p>
          <p class="area-caveat">
            SA2 statistical areas may cover part of a suburb or several suburbs.
          </p>
        </section>
        <aside
          v-if="!data.area.is_comparable"
          class="comparison-feedback"
          role="status"
        >
          This area is not eligible for comparison.
          {{ data.area.eligibility_note }}
        </aside>
        <section aria-labelledby="overview-title">
          <h2 id="overview-title" class="detail-section-title">
            Area overview
          </h2>
          <div class="overview-grid">
            <article
              v-for="measure in comparisonMeasures"
              :key="measure.key"
              :data-measure="measure.key"
            >
              <h3>
                <span class="category-icon"
                  ><SiteIcon :name="measure.icon" /></span
                >{{ measure.title }}
              </h3>
              <IndicatorValue :indicator="getIndicator(data, measure.key)" />
              <p class="overview-explanation">{{ measure.meaning }}</p>
            </article>
          </div>
        </section>
        <PopulationHistory
          :history="data.population_history"
          :sources="data.population_sources"
        />
        <aside class="data-note">
          <strong>Keep these measures in context</strong>
          <p>
            Census rent is historical. Transport and open-space measures remain
            provisional. Area-wide measures do not describe access from an
            individual rental property.
          </p>
        </aside>
        <div class="detail-actions">
          <NuxtLink :to="returnLocation" class="renter-button"
            >Back to comparison</NuxtLink
          ><NuxtLink
            v-if="data.area.is_comparable"
            :to="{ path: '/compare', query: { sa2: data.area.sa2_code } }"
            class="outline-button"
            >Compare with another area</NuxtLink
          ><NuxtLink v-else to="/" class="outline-button"
            >Explore other areas</NuxtLink
          >
        </div>
      </template>
    </main>
    <SiteFooter />
  </div>
</template>
