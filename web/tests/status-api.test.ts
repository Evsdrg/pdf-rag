import assert from 'node:assert/strict'
import { test } from 'node:test'
import { getLibraryStatus } from '../src/api.ts'

test('status endpoint forwards cancellation and exposes health diagnostics', async () => {
  const previous = globalThis.fetch
  const controller = new AbortController()
  let requested: URL | undefined
  let receivedSignal: AbortSignal | null | undefined
  const health = {
    status: 'ok', warnings: [], rows: 28385, table_version: 206,
    fts_index: ['text_idx'], vector_partitions: [{ table: 'vec_test', rows: 28385, indices: ['vector_idx'] }],
    disk_bytes: 307000000, data_bytes: 140000000, fragmentation_ratio: 2.16,
    last_ingest: null, entity_snapshot: { bytes: 6440042, mtime: 1 },
  }
  globalThis.fetch = async (input, init) => {
    requested = new URL(String(input), 'http://localhost')
    receivedSignal = init?.signal
    return new Response(JSON.stringify({ indexed: true, health }))
  }
  try {
    const response = await getLibraryStatus(controller.signal)
    assert.equal(requested.pathname, '/api/v2/status')
    assert.equal(receivedSignal, controller.signal)
    assert.equal(response.health.fragmentation_ratio, 2.16)
    assert.equal(response.health.entity_snapshot.bytes, 6440042)
  } finally {
    globalThis.fetch = previous
  }
})
