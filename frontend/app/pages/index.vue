<script setup>
import { endpointUrl, requestJson } from '~/utils/api.js'
const config = useRuntimeConfig()
const selected = ref([])
const activeCode = ref(null)
const selectionMessage = ref('')
const searchRevision = ref(0)
const selectedCodes = computed(() =>
  selected.value.map((area) => area.sa2_code),
)
const compareLocation = computed(() => ({
  path: '/compare',
  query: { sa2: selectedCodes.value.join(',') },
}))
function addArea(area) {
  if (!area.is_comparable) {
    selectionMessage.value = `${area.name} is not available for comparison because its recorded population is zero.`
    return
  }
  if (selectedCodes.value.includes(area.sa2_code)) {
    selectionMessage.value = `${area.name} is already selected.`
    activeCode.value = area.sa2_code
    return
  }
  if (selected.value.length >= 3) {
    selectionMessage.value =
      'Three areas are already selected. Remove one before choosing another.'
    return
  }
  selected.value = [...selected.value, area]
  activeCode.value = area.sa2_code
  selectionMessage.value = `${area.name} added. ${selected.value.length} of 3 areas selected.`
  searchRevision.value++
}
function removeArea(code) {
  const area = selected.value.find((item) => item.sa2_code === code)
  selected.value = selected.value.filter((item) => item.sa2_code !== code)
  activeCode.value = selected.value.at(-1)?.sa2_code || null
  selectionMessage.value = `${area?.name || 'Area'} removed. ${selected.value.length} of 3 areas selected.`
}
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
          <h2 id="start-title">Choose an area to start</h2>
          <p>
            Search by name or choose an area on the map, then add up to two
            more to compare.
          </p>
          <AreaSearch
            v-if="selected.length < 3"
            :key="searchRevision"
            :api-base="config.public.apiBase"
            :excluded="selectedCodes"
            label="Add an area"
            loading-hint="You can explore the map in the meantime."
            @select="addArea"
          />
          <p v-else class="selection-limit">
            Three areas selected. Remove one to choose another.
          </p>
          <div v-if="selected.length" class="selected-area">
            <div class="selected-heading">
              <SiteIcon name="pin" />
              <div>
                <span>YOUR SELECTED AREAS</span>
                <h3>{{ selected.length }} of 3 selected</h3>
              </div>
            </div>
            <div class="home-area-chips">
              <button
                v-for="area in selected"
                :key="area.sa2_code"
                :aria-label="`Remove ${area.name}`"
                @click="removeArea(area.sa2_code)"
              >
                {{ area.name }}<SiteIcon name="close" />
              </button>
            </div>
            <p v-if="selected.length === 1">
              Start here, or add another area to compare.
            </p>
            <p v-else>Your areas are ready to compare across the four measures.</p>
            <NuxtLink :to="compareLocation" class="renter-button"
              >{{
                selected.length === 1
                  ? 'View this area'
                  : `Compare ${selected.length} areas`
              }}
              <SiteIcon name="arrow" /></NuxtLink
            >
          </div>
          <div v-else class="search-hint">
            <SiteIcon name="pin" />
            <p>Select an area, then add up to two more to compare.</p>
          </div>
          <p class="selection-message" role="status" aria-live="polite">
            {{ selectionMessage }}
          </p>
          <p class="geography-note">
            We use SA2 statistical areas, which may cover part of a suburb or
            several suburbs.
          </p>
        </div>
        <div class="map-panel">
          <ClientOnly
            ><AreaMap
              :selected-codes="selectedCodes"
              :active-code="activeCode"
              @select="addArea"
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
          Rent figures are from 2021, not current listings. Transport coverage
          varies, and open-space results reflect selected public records. Use
          these area comparisons as a starting point alongside your budget,
          commute and visits.
        </p>
      </aside>
    </main>
    <SiteFooter />
  </div>
</template>
