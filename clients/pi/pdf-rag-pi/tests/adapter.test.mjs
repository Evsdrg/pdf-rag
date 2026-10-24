import assert from 'node:assert/strict';
import { readFile, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';

async function loadAdapter() {
  const source = await readFile(new URL('../extensions/pdf-rag.ts', import.meta.url), 'utf8');
  const directory = await mkdtemp(join(tmpdir(), 'pdfrag-pi-test-'));
  const file = join(directory, 'adapter.ts');
  const stub = `const Type = new Proxy({}, { get: () => (...args) => ({ args }) });`;
  await writeFile(file, source.replace('import { Type } from "typebox";', stub));
  try {
    return (await import(pathToFileURL(file).href)).default;
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

test('register ten read-only tools and preserve v2 JSON continuation', async () => {
  const adapter = await loadAdapter();
  const tools = new Map();
  adapter({ registerTool: (tool) => tools.set(tool.name, tool) });
  assert.equal(tools.size, 10);
  for (const tool of tools.values()) assert.equal(tool.annotations.readOnlyHint, true);
  const previous = globalThis.fetch;
  let requested;
  globalThis.fetch = async (url) => {
    requested = new URL(url);
    return new Response(JSON.stringify({ schema_version: 2, files: [], truncated: true, next_cursor: 'next' }));
  };
  try {
    const result = await tools.get('pdf_rag_list_files').execute('id', { model_no: 'ABC123', limit: 1, cursor: 'old' });
    assert.equal(requested.pathname, '/api/v2/files');
    assert.equal(requested.searchParams.get('cursor'), 'old');
    assert.equal(requested.searchParams.get('model_no'), 'ABC123');
    assert.equal(JSON.parse(result.content[0].text).next_cursor, 'next');
    assert.equal(result.details.schema_version, 2);
  } finally {
    globalThis.fetch = previous;
  }
});

test('render returns image content rather than base64 text', async () => {
  const adapter = await loadAdapter();
  const tools = new Map();
  adapter({ registerTool: (tool) => tools.set(tool.name, tool) });
  const previous = globalThis.fetch;
  let requested;
  globalThis.fetch = async (url) => {
    requested = new URL(url);
    return new Response(new Uint8Array([1, 2, 3]), { headers: { 'X-PDF-RAG-Metadata': '{"page":1}' } });
  };
  try {
    const result = await tools.get('pdf_rag_render_page').execute('id', { file: 'sample.pdf', page: 1, clip: [0, 0, 1, 1] });
    assert.equal(requested.pathname, '/api/v2/render');
    assert.equal(requested.searchParams.get('clip'), '[0,0,1,1]');
    assert.deepEqual(result.content.map((item) => item.type), ['text', 'image']);
    assert.equal(result.content[1].data, 'AQID');
    assert.equal(result.content[1].mimeType, 'image/jpeg');
    assert.equal(result.content[0].text, '{"page":1}');
  } finally {
    globalThis.fetch = previous;
  }
});

test('structured errors are not mistaken for document text', async () => {
  const adapter = await loadAdapter();
  const tools = new Map();
  adapter({ registerTool: (tool) => tools.set(tool.name, tool) });
  const previous = globalThis.fetch;
  globalThis.fetch = async () => new Response('{"error":{"code":"STALE_CURSOR"}}', { status: 400 });
  try {
    await assert.rejects(() => tools.get('pdf_rag_read_page').execute('id', { file: 'sample.pdf', page: 1 }), /STALE_CURSOR/);
  } finally {
    globalThis.fetch = previous;
  }
});
