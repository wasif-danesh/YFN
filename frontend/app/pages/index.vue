<script setup>
import { endpointUrl, requestJson } from '~/utils/api.js'
const config = useRuntimeConfig()
const selected = ref(null)
useSeoMeta({
  title: 'Find your place in Melbourne | Your Friendly Neighbourhood',
  description:
    'Explore Greater Melbourne areas and compare rent, public transport, population change and open space.',
})
const categories = [
  {
    icon: 'home',
    title: 'Rent',
    text: 'Compare median weekly rent reported in the 2021 Census.',
  },
  {
    icon: 'train',
    title: 'Public transport',
    text: 'Explore area-level public transport access.',
  },
  {
    icon: 'people',
    title: 'Population change',
    text: 'See how population changed from 2020 to 2025.',
  },
  {
    icon: 'leaf',
    title: 'Open space',
    text: 'Compare selected open space per resident.',
  },
]
onMounted(() => {
  // Wake the free-plan API while the visitor reads the page; search handles any failure.
  try {
    requestJson(endpointUrl(config.public.apiBase, 'health')).catch(() => {})
  } catch {
    /* An invalid API setting is reported by the search itself. */
  }
})
</script>
<template>
  <div class="renter-site">
    <SiteHeader />
    <main id="main" class="home-main">
      <section class="home-intro">
        <p class="eyebrow">FOR RENTERS NEW TO MELBOURNE</p>
        <h1>Find your place in Melbourne.</h1>
        <p>
          Explore local areas and compare rent, transport, population change and
          open space.
        </p>
      </section>
      <section class="explore-panel" aria-labelledby="start-title">
        <div class="search-panel">
          <span class="step-label">YOUR NEXT CHAPTER STARTS HERE</span>
          <h2 id="start-title">Start with an area</h2>
          <p>Search by name or choose an area on the map.</p>
          <AreaSearch
            :api-base="config.public.apiBase"
            loading-hint="You can explore the map in the meantime."
            @select="selected = $event"
          />
          <div v-if="selected" class="selected-area" aria-live="polite">
            <div class="selected-heading">
              <SiteIcon name="pin" />
              <div>
                <span>YOUR SELECTED AREA</span>
                <h3>{{ selected.name }}</h3>
              </div>
            </div>
            <p v-if="!selected.is_comparable">
              This area is not available for comparison because the recorded
              population is zero. Choose another area.
            </p>
            <template v-else
              ><p>Start here, then add another area to see how they compare.</p>
              <NuxtLink
                :to="{ path: '/compare', query: { sa2: selected.sa2_code } }"
                class="renter-button"
                >Compare this area <SiteIcon name="arrow" /></NuxtLink
            ></template>
          </div>
          <div v-else class="search-hint">
            <SiteIcon name="pin" />
            <p>Select an area, then add another to compare.</p>
          </div>
          <p class="geography-note">
            We use SA2 statistical areas, which may cover part of a suburb or
            several suburbs.
          </p>
        </div>
        <div class="map-panel">
          <ClientOnly
            ><AreaMap
              :selected-code="selected?.sa2_code"
              @select="selected = $event"
            /><template #fallback
              ><div class="map-placeholder" role="status">
                Loading the Greater Melbourne map…
              </div></template
            ></ClientOnly
          >
        </div>
      </section>
      <section class="perspectives" aria-labelledby="perspectives-title">
        <p class="eyebrow">LOOK BEYOND THE RENT</p>
        <h2 id="perspectives-title">Four perspectives. A clearer choice.</h2>
        <p class="section-subtitle">
          Understand the differences that matter for your everyday life.
        </p>
        <div class="category-grid">
          <article v-for="category in categories" :key="category.title">
            <h3>
              <span class="category-icon"
                ><SiteIcon :name="category.icon" /></span
              >{{ category.title }}
            </h3>
            <p>{{ category.text }}</p>
          </article>
        </div>
        <p class="data-caption">
          Source dates and coverage notes are available with each measure.
        </p>
      </section>
      <aside class="data-note">
        <strong>A little context for your search</strong>
        <p>
          Rent figures are from 2021, not current listings. Transport and
          open-space measures are provisional. Use these area comparisons as a
          starting point alongside your budget, commute and visits.
        </p>
      </aside>
    </main>
    <SiteFooter />
  </div>
</template>
