import { describe, it, expect, vi } from 'vitest'
import { endpointUrl, requestJson } from '../../app/utils/api.js'

const inputs = { query: 'Carl & %', compareCodes: '206041117,213031348', detailCode: '206041117' }
describe('API requests', () => {
  it('uses root health and encodes search/selection parameters', () => {
    expect(endpointUrl('https://api.example/api/v1/', 'health', inputs)).toBe('https://api.example/health')
    const search = new URL(endpointUrl('https://api.example/api/v1', 'search', inputs))
    expect(search.searchParams.get('query')).toBe(inputs.query)
    expect(endpointUrl('https://api.example/api/v1', 'details', inputs)).toBe('https://api.example/api/v1/areas/206041117')
  })
  it('rejects malformed API configuration', () => {
    expect(() => endpointUrl('https://api.example', 'health', inputs)).toThrow()
    expect(() => endpointUrl('file:///api/v1', 'health', inputs)).toThrow()
  })
  it('preserves backend error JSON and status', async () => {
    const fetcher = vi.fn().mockResolvedValue({ status: 422, ok: false, text: async () => '{"error":{"code":"INVALID_SELECTION"}}' })
    const result = await requestJson('/test', { fetcher })
    expect(result.status).toBe(422)
    expect(result.body.error.code).toBe('INVALID_SELECTION')
  })
  it('preserves non-JSON error output', async () => {
    const fetcher = vi.fn().mockResolvedValue({ status: 502, ok: false, text: async () => 'Bad gateway' })
    expect((await requestJson('/test', { fetcher })).body).toBe('Bad gateway')
  })
  it('aborts stalled requests', async () => {
    const fetcher = (_, { signal }) => new Promise((resolve, reject) => signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError'))))
    await expect(requestJson('/test', { fetcher, timeoutMs: 5 })).rejects.toMatchObject({ name: 'AbortError' })
  })
})
