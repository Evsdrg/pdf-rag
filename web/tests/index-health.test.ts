import assert from 'node:assert/strict'
import { test } from 'node:test'
import { coveragePercentage, ingestFinishedSince } from '../src/indexHealth.ts'

test('partial source coverage never rounds up to 100 percent', () => {
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: 386, indexed_files: 385 }), 99.7)
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: 2, indexed_files: 2 }), 100)
})

test('unavailable source inventory means unknown coverage rather than 100 percent', () => {
  assert.equal(coveragePercentage({ source_status: 'unavailable', source_files: null, indexed_files: 385 }), null)
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: null, indexed_files: 385 }), null)
})

test('a new ingest completion marker triggers a health refresh, repeat polls do not', () => {
  assert.equal(ingestFinishedSince('2026-11-10T10:00:00', '2026-11-10T10:05:00'), true)
  assert.equal(ingestFinishedSince('2026-11-10T10:05:00', '2026-11-10T10:05:00'), false)
  // 运行中/空状态不写 finished_at,不能当成新入库。
  assert.equal(ingestFinishedSince('2026-11-10T10:00:00', undefined), false)
  // 基线还没有完成记录时,第一次真实完成应当刷新。
  assert.equal(ingestFinishedSince(undefined, '2026-11-10T10:05:00'), true)
})
