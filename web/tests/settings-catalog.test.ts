import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { commonNames, matchesSetting, sectionOf, sections } from '../src/components/settings/catalog.ts'
import type { ConfigSpec } from '../src/api.ts'

const spec: ConfigSpec = {
  label: '索引 OCR 并发数', value: 4, default: 4, kind: 'int', group: '索引吞吐',
  desc: '整轮索引共用的页面请求通路数', env_key: 'OCR_WORKERS', lo: 1, hi: 32, overridden: false,
}

test('catalog covers all backend settings once', () => {
  const backend = readFileSync(new URL('../../backend/config.py', import.meta.url), 'utf8')
  const registered = Array.from(backend.matchAll(/Spec\("([a-z_]+)"/g), (match) => match[1])
  const names = sections.flatMap((section) => [...section.primary, ...section.advanced])
  assert.equal(names.length, new Set(names).size)
  assert.deepEqual([...names].sort(), registered.sort())
})

test('parallel settings are first-class and not hidden in advanced settings', () => {
  const indexing = sections.find((section) => section.id === 'index')!
  assert.deepEqual(indexing.primary.slice(0, 2), ['extract_workers', 'ocr_workers'])
  assert.ok(commonNames.includes('extract_workers'))
  assert.ok(commonNames.includes('ocr_workers'))
})

test('search accepts label, variable, environment key and task category', () => {
  for (const query of ['并发', 'ocr_workers', 'OCR_WORKERS', '索引与并发', 'OCR 并发', '页面请求']) {
    assert.ok(matchesSetting('ocr_workers', spec, query), query)
  }
  assert.equal(matchesSetting('ocr_workers', spec, '不存在的配置'), false)
})

test('advanced settings stay searchable and assigned to a task category', () => {
  const advanced: ConfigSpec = { ...spec, label: '融合平滑常数', desc: 'RRF 融合常数', env_key: 'RRF_K', group: '检索融合' }
  assert.equal(sectionOf('rrf_k')?.id, 'retrieval')
  assert.ok(matchesSetting('rrf_k', advanced, 'rrf_k'))
  assert.equal(sectionOf('future_setting'), undefined)
})
