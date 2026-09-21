<script setup>
import { computed, onMounted, reactive } from 'vue'
import { endpointUrl, endpoints, requestJson } from '../utils/api.js'

const props = defineProps({ apiBase: { type: String, required: true } })
const inputs = reactive({ query: 'carl', compareCodes: '206041117,213031348', detailCode: '206041117' })
const results = reactive(Object.fromEntries(endpoints.map(({ key }) => [key,
  { loading: false, status: null, ok: false, body: null, error: '', url: '' }])))
const busy = computed(() => Object.values(results).some(result => result.loading))
const successCount = computed(() => Object.values(results).filter(result => result.ok).length)

async function run(key) {
  const result = results[key]
  if (result.loading) return
  Object.assign(result, { loading: true, status: null, ok: false, body: null, error: '', url: '' })
  try {
    result.url = endpointUrl(props.apiBase, key, inputs)
    Object.assign(result, await requestJson(result.url))
  } catch (error) {
    result.error = error.name === 'AbortError'
      ? 'Request timed out. The API may be starting up. Please retry.'
      : 'Could not reach the API. Check the API URL, server status and allowed frontend origin, then retry.'
  } finally {
    result.loading = false
  }
}

async function runAll() {
  await Promise.all(endpoints.map(({ key }) => run(key)))
}

function statusLabel(key) {
  const result = results[key]
  if (result.loading) return 'Loading…'
  if (result.error) return 'Connection error'
  return result.status ? `HTTP ${result.status}` : 'Not run'
}

onMounted(runAll)
</script>

<template>
  <div class="console-shell">
    <a class="skip-link" href="#main">Skip to API results</a>
    <header class="site-header">
      <a class="brand" href="/">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10 12 2l9 8v11h-7v-7h-4v7H3Z" /></svg>
        Your Friendly Neighbourhood
      </a>
      <span class="test-label">Integration test</span>
    </header>

    <main id="main" class="page-container">
      <div class="eyebrow">DEVELOPER WORKSPACE</div>
      <h1>One page. Four API checks.</h1>
      <p class="intro">Test the connection between our frontend, FastAPI service and Greater Melbourne database.</p>
      <aside class="notice"><strong>Test interface — not the renter homepage.</strong> Real development data is shown below. Transport and open-space measures remain provisional; a healthy API does not mean the data is approved for publication.</aside>

      <section class="controls" aria-labelledby="request-settings">
        <div class="section-heading"><div><h2 id="request-settings">Request settings</h2><p>Calls run automatically when this page opens.</p></div>
          <button class="primary-button" :disabled="busy" @click="runAll">{{ busy ? 'Running checks…' : 'Run all APIs' }}</button>
        </div>
        <div class="input-grid">
          <label>Search by area name<input v-model="inputs.query" :disabled="busy" maxlength="100" placeholder="e.g. carl" /></label>
          <label>Comparison SA2 codes<input v-model="inputs.compareCodes" :disabled="busy" placeholder="206041117,213031348" /><small>Two or three codes, separated by commas.</small></label>
          <label>Area Details SA2 code<input v-model="inputs.detailCode" :disabled="busy" placeholder="206041117" /><small>206041117 is Carlton.</small></label>
        </div>
        <p class="api-address"><strong>API base:</strong> <code>{{ apiBase }}</code></p>
        <p class="startup-note">The Free Render API can take a little time to wake up. Requests wait up to 90 seconds; each result can be retried.</p>
      </section>

      <div class="results-heading"><h2>API responses</h2><p role="status">{{ successCount }} of 4 requests successful</p></div>
      <div class="result-grid">
        <section v-for="endpoint in endpoints" :key="endpoint.key" class="result-card" :aria-labelledby="`title-${endpoint.key}`" :aria-busy="results[endpoint.key].loading" :data-testid="endpoint.key">
          <div class="result-header"><div><h3 :id="`title-${endpoint.key}`">{{ endpoint.title }}</h3><p>{{ endpoint.description }}</p></div>
            <span class="status" :class="{ success: results[endpoint.key].ok, failed: results[endpoint.key].error || (results[endpoint.key].status && !results[endpoint.key].ok) }" role="status">{{ statusLabel(endpoint.key) }}</span>
          </div>
          <div class="request-path"><span>GET</span><code>{{ results[endpoint.key].url || 'Ready to request' }}</code></div>
          <div v-if="results[endpoint.key].loading" class="empty-output">Waiting for the API…</div>
          <p v-else-if="results[endpoint.key].error" class="request-error" role="alert">{{ results[endpoint.key].error }}</p>
          <pre v-else-if="results[endpoint.key].body !== null" tabindex="0" :aria-label="`${endpoint.title} JSON output`">{{ JSON.stringify(results[endpoint.key].body, null, 2) }}</pre>
          <div v-else class="empty-output">No response yet.</div>
          <div class="result-footer"><span>JSON response</span><button :disabled="results[endpoint.key].loading" :aria-label="`Run ${endpoint.title}`" @click="run(endpoint.key)">{{ results[endpoint.key].loading ? 'Loading…' : 'Run request' }}</button></div>
        </section>
      </div>
      <footer class="page-footer">Your Friendly Neighbourhood <span>Read-only API · No database changes</span></footer>
    </main>
  </div>
</template>
