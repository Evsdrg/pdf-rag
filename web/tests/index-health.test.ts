import assert from 'node:assert/strict'
import { test } from 'node:test'
import { coveragePercentage } from '../src/indexHealth.ts'

test('partial source coverage never rounds up to 100 percent', () => {
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: 386, indexed_files: 385 }), 99.7)
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: 2, indexed_files: 2 }), 100)
})

test('unavailable source inventory means unknown coverage rather than 100 percent', () => {
  assert.equal(coveragePercentage({ source_status: 'unavailable', source_files: null, indexed_files: 385 }), null)
  assert.equal(coveragePercentage({ source_status: 'ok', source_files: null, indexed_files: 385 }), null)
})
