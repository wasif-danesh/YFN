<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import 'leaflet/dist/leaflet.css'
const props = defineProps({ selectedCode: { type: String, default: null } })
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
  const selected = feature.properties.sa2_code === props.selectedCode
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
  if (area.is_comparable) {
    const link = document.createElement('a')
    link.href = `/compare?sa2=${encodeURIComponent(area.sa2_code)}`
    link.textContent = 'Compare this area →'
    link.className = 'map-compare-link'
    content.append(link)
  }
  layer.bindPopup(content, { maxWidth: 240 }).openPopup()
}
function showSelected() {
  if (!boundaries) return
  boundaries.setStyle(style)
  const layer = layers.get(props.selectedCode)
  if (!layer) return
  layer.bringToFront()
  map.fitBounds(layer.getBounds(), {
    padding: [70, 70],
    maxZoom: 13,
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
          if (feature.properties.sa2_code !== props.selectedCode)
            layer.setStyle({ fillOpacity: 0.5, weight: 2 })
        })
        layer.on('mouseout', () => layer.setStyle(style(feature)))
      },
    }).addTo(map)
    reset()
    showSelected()
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
watch(() => props.selectedCode, showSelected)
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
      aria-describedby="map-instructions"
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
    <div class="map-caption">
      <span id="map-instructions"
        >Choose an area to begin. Use search for keyboard selection.</span
      ><a
        href="https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files"
        target="_blank"
        rel="noopener noreferrer"
        >Boundaries: ABS, 2021 · CC BY 4.0</a
      >
    </div>
  </div>
</template>
