<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import 'leaflet/dist/leaflet.css'
const props = defineProps({
  selectedCodes: { type: Array, default: () => [] },
  activeCode: { type: String, default: null },
  // Set to '' on a read-only, single-area map where picking areas isn't offered.
  instructions: {
    type: String,
    default: 'Choose up to three areas. Use search for keyboard selection.',
  },
  // Set to false only where the ABS boundary attribution already appears
  // elsewhere on the same page (CC BY 4.0 requires it to appear somewhere,
  // not on every instance of the map).
  showAttribution: { type: Boolean, default: true },
})
const emit = defineEmits(['select'])
const container = ref(null),
  loading = ref(true),
  error = ref(''),
  tileError = ref(false)
let map,
  boundaries,
  L,
  resizeObserver,
  disposed = false
const layers = new Map()
const controller = new AbortController()
function style(feature) {
  const selected = props.selectedCodes.includes(feature.properties.sa2_code)
  return {
    color: selected ? '#0754c9' : '#6486ad',
    weight: selected ? 2.5 : 1,
    fillColor: selected
      ? '#1765d8'
      : feature.properties.is_comparable
        ? '#d5e5f5'
        : '#a5aeb9',
    fillOpacity: selected ? 0.72 : 0.25,
  }
}
function popup(layer) {
  map?.closePopup()
  if (layer.getPopup()) {
    layer.openPopup()
    return
  }
  const area = layer.feature.properties
  const content = document.createElement('div')
  const heading = document.createElement('strong')
  heading.textContent = area.name
  content.append(heading)
  const note = document.createElement('p')
  note.textContent = area.is_comparable
    ? 'SA2 area · 2021 boundaries'
    : 'Not available for comparison'
  content.append(note)
  layer.bindPopup(content, { maxWidth: 240 }).openPopup()
}
function showSelection() {
  if (!boundaries) return
  boundaries.setStyle(style)
  if (!props.activeCode) {
    if (!props.selectedCodes.length) reset()
    return
  }
  const layer = layers.get(props.activeCode)
  if (!layer) return
  layer.bringToFront()
  map.fitBounds(layer.getBounds(), {
    padding: [70, 70],
    maxZoom: 10.5,
    animate: false,
  })
  popup(layer)
}
function reset() {
  if (map && boundaries) {
    map.closePopup()
    map.fitBounds(boundaries.getBounds(), { padding: [15, 15], animate: false })
  }
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    L = await import('leaflet')
    const response = await fetch('/maps/greater-melbourne-sa2.geojson', {
      signal: controller.signal,
    })
    if (!response.ok) throw new Error('Map unavailable')
    const data = await response.json()
    if (disposed) return
    map = L.map(container.value, {
      scrollWheelZoom: false,
      zoomControl: false,
      zoomSnap: 0.25,
      zoomDelta: 0.5,
      minZoom: 8,
      maxZoom: 17,
    })
    L.control.zoom({ position: 'topright' }).addTo(map)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    })
      .on('tileerror', () => {
        tileError.value = true
      })
      .addTo(map)
    boundaries = L.geoJSON(data, {
      style,
      onEachFeature(feature, layer) {
        layers.set(feature.properties.sa2_code, layer)
        const text = document.createElement('span')
        text.textContent = feature.properties.name
        layer.bindTooltip(text, { sticky: true })
        layer.on('click', () => {
          emit('select', feature.properties)
          popup(layer)
        })
        layer.on('mouseover', () => {
          if (!props.selectedCodes.includes(feature.properties.sa2_code))
            layer.setStyle({ fillOpacity: 0.5, weight: 2 })
        })
        layer.on('mouseout', () => layer.setStyle(style(feature)))
      },
    }).addTo(map)
    reset()
    showSelection()
    // Search provides an equivalent keyboard route without 361 polygon tab stops.
    boundaries.eachLayer((layer) => {
      const path = layer.getElement()
      if (path) {
        path.setAttribute('aria-label', layer.feature.properties.name)
        path.dataset.sa2 = layer.feature.properties.sa2_code
      }
    })
    resizeObserver = new ResizeObserver(() => map?.invalidateSize())
    resizeObserver.observe(container.value)
  } catch (cause) {
    if (!disposed) {
      map?.remove()
      map = null
      layers.clear()
      boundaries = null
      error.value = 'The map couldn’t load. You can still search by area name.'
    }
  } finally {
    if (!disposed) loading.value = false
  }
}
watch(
  () => [props.selectedCodes, props.activeCode],
  showSelection,
  { deep: true },
)
onMounted(load)
onBeforeUnmount(() => {
  disposed = true
  controller.abort()
  resizeObserver?.disconnect()
  map?.remove()
  map = null
})
</script>
<template>
  <div class="area-map">
    <div
      ref="container"
      class="map-canvas"
      aria-label="Interactive Greater Melbourne SA2 map"
      :aria-describedby="instructions ? 'map-instructions' : undefined"
    ></div>
    <button v-if="!loading && !error" class="map-reset" @click="reset">
      Reset view
    </button>
    <div v-if="loading || error" class="map-overlay">
      <p :role="error ? 'alert' : 'status'">
        {{ error || 'Loading Greater Melbourne areas…' }}
      </p>
      <button v-if="error" class="text-button" @click="load">Retry map</button>
    </div>
    <p v-if="tileError && !error" class="tile-notice" role="status">
      Street map tiles couldn’t load. Area boundaries still work.
    </p>
    <div v-if="instructions || showAttribution" class="map-caption">
      <span v-if="instructions" id="map-instructions">{{
        instructions
      }}</span
      ><a
        v-if="showAttribution"
        href="https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files"
        target="_blank"
        rel="noopener noreferrer"
        >Boundaries: ABS, 2021 · CC BY 4.0</a
      >
    </div>
  </div>
</template>
