<script setup>
import { endpointUrl, requestJson } from '~/utils/api.js'
import { selectionCodes } from '~/utils/areas.js'
import { rentDifference, detailsLocation } from '~/utils/comparison.js'
const route = useRoute(),
  router = useRouter(),
  config = useRuntimeConfig()
const entries = ref([]),
  loading = ref(false),
  error = ref(''),
  message = ref(''),
  knownAreas = ref({}),
  search = ref(null)
let revision = 0,
  disposed = false,
  controller
const codes = computed(() => {
  try {
    return selectionCodes(route.query.sa2)
  } catch {
    return []
  }
})
const rentSummary = computed(() => rentDifference(entries.value))
useSeoMeta({
  title: 'Compare Melbourne areas | Your Friendly Neighbourhood',
  description:
    'Compare two or three Melbourne areas across rent, transport, population change and open space, with source dates and limitations.',
})
async function load() {
  const current = ++revision
  controller?.abort()
  controller = new AbortController()
  entries.value = []
  error.value = ''
  loading.value = false
  try {
    const selected = selectionCodes(route.query.sa2)
    if (!selected.length) return
    loading.value = true
    const response = await requestJson(
      endpointUrl(
        config.public.apiBase,
        selected.length === 1 ? 'details' : 'compare',
        { detailCode: selected[0], compareCodes: selected.join(',') },
      ),
      { signal: controller.signal },
    )
    if (disposed || current !== revision) return
    if (!response.ok)
      throw new Error(
        response.body?.error?.message ||
          'We couldn’t load these areas. Please try again.',
      )
    const data = selected.length === 1 ? [response.body] : response.body.areas
    if (data.some((entry) => !entry.area.is_comparable))
      throw new Error(
        'This area is not available for comparison. Remove it and choose another area.',
      )
    entries.value = data
    for (const entry of data)
      knownAreas.value[entry.area.sa2_code] = entry.area.name
  } catch (cause) {
    if (!disposed && current === revision)
      error.value =
        cause instanceof TypeError || cause.name === 'AbortError'
          ? 'We couldn’t reach the service. It may be waking up. Please try again.'
          : cause.message
  } finally {
    if (!disposed && current === revision) loading.value = false
  }
}
async function add(area) {
  if (
    codes.value.length >= 3 ||
    codes.value.includes(area.sa2_code) ||
    !area.is_comparable
  )
    return
  knownAreas.value[area.sa2_code] = area.name
  await router.push({
    path: '/compare',
    query: { sa2: [...codes.value, area.sa2_code].join(',') },
  })
  message.value = `${area.name} added. ${codes.value.length} of 3 areas selected.`
  await nextTick()
  // Adding a third removes the search control; move focus to a persistent heading.
  if (codes.value.length === 3)
    document.getElementById('selection-title')?.focus()
}
async function remove(code) {
  const name = knownAreas.value[code] || code
  const remaining = codes.value.filter((item) => item !== code)
  await router.push({
    path: '/compare',
    query: remaining.length ? { sa2: remaining.join(',') } : {},
  })
  message.value = `${name} removed. ${remaining.length} of 3 areas selected.`
  await nextTick()
  search.value?.focusInput()
}
watch(() => route.query.sa2, load)
onMounted(load)
onBeforeUnmount(() => {
  disposed = true
  revision++
  controller?.abort()
})
</script>
<template>
  <div class="renter-site">
    <SiteHeader />
    <main id="main" class="home-main compare-main">
      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <NuxtLink to="/">Home</NuxtLink><span aria-hidden="true">/</span
        ><span aria-current="page">Compare areas</span>
      </nav>
      <section class="home-intro">
        <h1>Compare Melbourne areas</h1>
        <p>See how two or three areas differ across the same four measures.</p>
      </section>
      <section
        class="comparison-controls completed-controls"
        aria-labelledby="selection-title"
      >
        <h2 id="selection-title" tabindex="-1">
          {{
            codes.length === 1
              ? 'Add another area to compare'
              : 'Choose your areas'
          }}
        </h2>
        <AreaSearch
          v-if="codes.length < 3"
          ref="search"
          id="compare-search"
          label="Add an area"
          :api-base="config.public.apiBase"
          :excluded="codes"
          @select="add"
        />
        <p v-else class="selection-limit">
          Three areas selected. Remove one to choose another.
        </p>
        <div class="area-chips">
          <button
            v-for="code in codes"
            :key="code"
            @click="remove(code)"
            :aria-label="`Remove ${knownAreas[code] || code}`"
          >
            {{ knownAreas[code] || code }}<SiteIcon name="close" /></button
          ><button
            v-if="codes.length > 0 && codes.length < 3"
            class="add-another"
            @click="search?.focusInput()"
          >
            + {{ codes.length === 2 ? 'Add a third area' : 'Add another area' }}
          </button>
        </div>
        <div class="selection-summary">
          <span>{{ codes.length }} of 3 areas selected</span
          ><span>Transport and open-space measures are provisional.</span>
        </div>
        <p class="sr-only" role="status">{{ message }}</p>
      </section>
      <section aria-labelledby="comparison-title" :aria-busy="loading">
        <div class="comparison-section-heading">
          <h2 id="comparison-title">Your comparison</h2>
          <NuxtLink
            v-if="route.query.sa2 != null"
            to="/compare"
            class="text-button"
            >Clear selection</NuxtLink
          >
        </div>
        <LoadingStatus
          v-if="loading"
          class="comparison-feedback"
          label="Loading your areas…"
        />
        <div v-else-if="error" class="comparison-feedback">
          <p role="alert">{{ error }}</p>
          <button class="text-button" @click="load">Try again</button>
        </div>
        <div v-else-if="!entries.length" class="comparison-empty">
          <SiteIcon name="pin" />
          <h3>A fresh start, one area at a time.</h3>
          <p>
            Search above to add your first area, or
            <NuxtLink to="/">explore the homepage map</NuxtLink>.
          </p>
        </div>
        <template v-else
          ><p
            v-if="entries.length === 1"
            class="single-area-note"
            role="status"
          >
            Here is your first area. Add a second to see them side by side.
          </p>
          <ComparisonTable :entries="entries"
        /></template>
      </section>
      <aside
        v-if="entries.length >= 2"
        class="rent-insight"
        aria-labelledby="rent-title"
      >
        <SiteIcon name="home" />
        <div>
          <h2 id="rent-title">Rent difference</h2>
          <p>
            {{
              rentSummary ||
              'A rent difference is not shown because one or more values are missing, limited or use different reference periods.'
            }}
          </p>
          <p>
            Compare the other measures alongside rent to understand the
            trade-offs. These historical figures do not describe current prices
            or potential savings.
          </p>
        </div>
      </aside>
      <section
        v-if="entries.length"
        class="explore-details"
        aria-labelledby="explore-details-title"
      >
        <h2 id="explore-details-title">Explore an area in detail</h2>
        <div class="area-detail-links">
          <article v-for="entry in entries" :key="entry.area.sa2_code">
            <h3>
              <span class="category-icon"><SiteIcon name="home" /></span
              >{{ entry.area.name }}
            </h3>
            <p>View population history, source dates and coverage notes.</p>
            <NuxtLink
              :to="detailsLocation(entry.area.sa2_code, codes)"
              class="outline-button"
              >View {{ entry.area.name }} details <SiteIcon name="arrow"
            /></NuxtLink>
          </article>
        </div>
      </section>
      <aside class="data-note">
        <strong>Compare with context</strong>
        <p>
          SA2s may cover part of a suburb or several suburbs. Unknown values are
          shown as “Not available”. There is no overall best-area score. Check
          current listings and your own travel needs alongside these dated
          measures.
        </p>
      </aside>
    </main>
    <SiteFooter />
  </div>
</template>
