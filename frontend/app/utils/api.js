export const endpoints = [
  {
    key: 'health',
    title: 'Service health',
    description: 'Can the API read the database?',
  },
  {
    key: 'search',
    title: 'Area search',
    description: 'Find comparable areas by official SA2 name.',
  },
  {
    key: 'compare',
    title: 'Compare areas',
    description: 'Read four indicators for two or three areas.',
  },
  {
    key: 'details',
    title: 'Area details',
    description: 'Read indicators, sources and annual population counts.',
  },
]

export function endpointUrl(apiBase, key, inputs) {
  const base = new URL(apiBase)
  if (
    !['http:', 'https:'].includes(base.protocol) ||
    base.username ||
    base.password ||
    base.search ||
    base.hash ||
    base.pathname.replace(/\/$/, '') !== '/api/v1'
  ) {
    throw new Error('API base must be an HTTP(S) URL ending in /api/v1.')
  }
  const root = base.href.replace(/\/$/, '')
  if (key === 'health') return `${root}/status`
  if (key === 'search')
    return `${root}/areas?${new URLSearchParams({ query: inputs.query, limit: '20' })}`
  if (key === 'compare')
    return `${root}/compare?${new URLSearchParams({ sa2: inputs.compareCodes })}`
  if (key === 'details')
    return `${root}/areas/${encodeURIComponent(inputs.detailCode)}`
  throw new Error('Unknown endpoint.')
}

export async function requestJson(
  url,
  { fetcher = fetch, timeoutMs = 90000, signal } = {},
) {
  const controller = new AbortController()
  const cancel = () => controller.abort()
  if (signal?.aborted) cancel()
  else signal?.addEventListener('abort', cancel, { once: true })
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetcher(url, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    })
    const text = await response.text()
    let body
    try {
      body = JSON.parse(text)
    } catch {
      body = text
    }
    return { status: response.status, ok: response.ok, body }
  } finally {
    clearTimeout(timeout)
    signal?.removeEventListener('abort', cancel)
  }
}
