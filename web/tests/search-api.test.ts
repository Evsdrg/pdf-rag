import assert from 'node:assert/strict'
import { test } from 'node:test'
import { searchDocs } from '../src/api.ts'

test('search defaults structured expansion off and explicitly forwards opt-in', async () => {
  const previous = globalThis.fetch
  const requests: URL[] = []
  const signal = new AbortController().signal
  globalThis.fetch = async (input, init) => {
    requests.push(new URL(String(input), 'http://localhost'))
    assert.equal(init?.signal, signal)
    return new Response(JSON.stringify({ results: [], structured: { enabled: false, status: 'disabled' } }))
  }
  try {
    await searchDocs('QMC6309', undefined, 5, 'fts', false, undefined, 0, signal)
    await searchDocs('QMC6309', 'sensors', 5, 'fts', false, 'A_1%', 0, signal, true)
    assert.equal(requests[0].searchParams.get('structured'), 'false')
    assert.equal(requests[1].searchParams.get('structured'), 'true')
    assert.equal(requests[1].pathname, '/api/v2/search')
    assert.equal(requests[1].searchParams.get('file'), 'A_1%')
    assert.equal(requests[1].searchParams.get('category'), 'sensors')
  } finally {
    globalThis.fetch = previous
  }
})
