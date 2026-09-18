<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { endpointUrl, requestJson } from '../utils/api.js'
import LoadingStatus from './LoadingStatus.vue'
const props = defineProps({
  apiBase: { type: String, required: true },
  id: { type: String, default: 'area-search' },
  excluded: { type: Array, default: () => [] },
  label: { type: String, default: 'Search for an area' },
  loadingHint: { type: String, default: '' },
})
const emit = defineEmits(['select'])
const query = ref(''),
  results = ref([]),
  open = ref(false),
  loading = ref(false),
  error = ref(''),
  active = ref(-1)
let timer,
  revision = 0,
  disposed = false
async function search() {
  const current = ++revision
  loading.value = true
  error.value = ''
  results.value = []
  active.value = -1
  try {
    const response = await requestJson(
      endpointUrl(props.apiBase, 'search', { query: query.value }),
    )
    if (disposed || current !== revision) return
    if (!response.ok) throw new Error('Search unavailable')
    results.value = response.body.areas
      .filter((area) => !props.excluded.includes(area.sa2_code))
      .slice(0, 8)
  } catch {
    if (!disposed && current === revision)
      error.value =
        'We couldn’t load areas. The service may be waking up. Please try again.'
  } finally {
    if (!disposed && current === revision) loading.value = false
  }
}
watch(query, () => {
  clearTimeout(timer)
  revision++
  results.value = []
  active.value = -1
  error.value = ''
  loading.value = true
  open.value = true
  timer = setTimeout(search, 250)
})
watch(active, async (index) => {
  await nextTick()
  if (index >= 0)
    document
      .getElementById(`${props.id}-option-${index}`)
      ?.scrollIntoView?.({ block: 'nearest' })
})
function choose(area) {
  if (props.excluded.includes(area.sa2_code)) return
  clearTimeout(timer)
  revision++
  loading.value = false
  open.value = false
  emit('select', area)
}
function focus() {
  open.value = true
  if (!results.value.length && !loading.value) search()
}
function keyboard(event) {
  if (event.key === 'Escape') {
    open.value = false
    return
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    open.value = true
    if (results.value.length)
      active.value =
        (active.value +
          (event.key === 'ArrowDown' ? 1 : -1) +
          results.value.length) %
        results.value.length
  }
  if (event.key === 'Enter' && open.value && active.value >= 0) {
    event.preventDefault()
    choose(results.value[active.value])
  }
}
watch(
  () => props.excluded,
  () => {
    results.value = results.value.filter(
      (area) => !props.excluded.includes(area.sa2_code),
    )
    active.value = -1
  },
)
function focusInput() {
  document.getElementById(props.id)?.focus()
}
defineExpose({ focusInput })
onBeforeUnmount(() => {
  disposed = true
  revision++
  clearTimeout(timer)
})
</script>
<template>
  <div
    class="area-search"
    @focusout="
      (event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) open = false
      }
    "
  >
    <label :for="id">{{ label }}</label>
    <div class="search-input">
      <SiteIcon name="search" /><input
        :id="id"
        v-model="query"
        role="combobox"
        autocomplete="off"
        maxlength="100"
        placeholder="e.g. Carlton or Footscray"
        :aria-expanded="open"
        aria-autocomplete="list"
        :aria-controls="`${id}-options`"
        :aria-activedescendant="
          open && active >= 0 ? `${id}-option-${active}` : undefined
        "
        @focus="focus"
        @keydown="keyboard"
      />
    </div>
    <div v-if="open" class="search-menu">
      <LoadingStatus
        v-if="loading"
        class="search-message"
        label="Loading areas…"
        :hint="loadingHint"
      />
      <div v-else-if="error" class="search-message">
        <p role="alert">{{ error }}</p>
        <button class="text-button" @click="search">Try again</button>
      </div>
      <p v-else-if="!results.length" role="status" class="search-message">
        No matching areas. Try an official SA2 name.
      </p>
      <ul :id="`${id}-options`" role="listbox" aria-label="Matching areas">
        <li
          v-for="(area, index) in results"
          :id="`${id}-option-${index}`"
          :key="area.sa2_code"
          role="option"
          :aria-selected="index === active"
          :class="{ highlighted: index === active }"
          @mousedown.prevent
          @click="choose(area)"
        >
          <strong>{{ area.name }}</strong
          ><span>SA2 area</span>
        </li>
      </ul>
    </div>
    <span class="sr-only" role="status">{{
      !loading && open && !error
        ? `${results.length} areas found. Use arrow keys and Enter to select.`
        : ''
    }}</span>
  </div>
</template>
