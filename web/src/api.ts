const BASE = '/api'

export interface Stats {
  indexed: boolean
  files: number
  chunks: number
  categories: { name: string; chunks: number }[]
  last_index: string | null
  history: HistoryEntry[]
  skipped: string[]
}

export interface HistoryEntry {
  time: string
  added: number
  removed: number
  chunks: number
  elapsed: number
  skipped: string[]
}

export interface IngestState {
  phase: string
  total_files?: number
  extract?: { done: number; total: number }
  embed?: { done: number; total: number }
  chunks?: number
  db_size_mb?: number
  elapsed?: number
  current?: string
  errors?: string[]
  skipped?: string[]
  finished_at?: string
}

export interface SearchHit {
  file: string
  page: number
  category: string
  model_no: string
  product?: string
  kind?: 'pdf' | 'md'
  c_id: string
  version?: string
  score: number
  snippet: string
}

export interface FileEntry {
  file: string
  category: string
  model_no: string
  product?: string
  kind?: 'pdf' | 'md'
  c_id: string
  pages: number
  chunks: number
}

/** 逐文档提取质量体检项 */
export interface ExtractReportItem {
  file: string
  category: string
  model_no: string
  pages: number
  chunks: number
  chars: number
  chars_per_page: number
  /** 每页字符数低于阈值:入库后基本不可检索,建议重跑提取/OCR */
  suspect: boolean
}

/** 单个可调参数:值 + 元数据,前端据此选控件并校验 */
export interface ConfigSpec {
  /** 面向人的中文名;name(对象键)才是机器标识符 */
  label: string
  value: number | boolean | string
  default: number | boolean | string
  kind: 'int' | 'float' | 'bool' | 'str'
  group: string
  desc: string
  env_key: string
  lo: number | null
  hi: number | null
  /** 是否已被运行时覆盖(不同于 .env/默认值) */
  overridden: boolean
}

export interface ConfigPayload {
  specs: Record<string, ConfigSpec>
  groups: string[]
}

/** OCR 状态:配置 + 最近一次真实调用的结果(后端不做任何主动探测) */
export interface OcrHealth {
  backend: 'local' | 'remote' | string
  url: string
  model?: string
  last_call: {
    ok: boolean
    at: string
    elapsed_s: number
    error: string
  } | null
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const r = await fetch(BASE + path, { signal })
  if (!r.ok) throw new Error(await errorText(r))
  return r.json() as Promise<T>
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!r.ok) throw new Error(await errorText(r))
  return r.json() as Promise<T>
}

async function del<T>(path: string): Promise<T> {
  const r = await fetch(BASE + path, { method: 'DELETE' })
  if (!r.ok) throw new Error(await errorText(r))
  return r.json() as Promise<T>
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(await errorText(r))
  return r.json() as Promise<T>
}

/** 后端用 HTTPException 返回可读原因(如取值超范围),尽量透出给用户 */
async function errorText(r: Response): Promise<string> {
  const detail = await r.json().catch(() => null)
  return detail?.detail ?? `${r.status} ${r.statusText}`
}

export const getState = () => get<IngestState>('/state')
export const getStats = () => get<Stats>('/stats')
export const getCategories = () => get<string[]>('/categories')
export const getFiles = (category?: string) =>
  get<FileEntry[]>('/files' + (category ? `?category=${encodeURIComponent(category)}` : ''))

// ---------- SWR(stale-while-revalidate)----------
// 文件库/资料库这类页面每次切入都全量重拉没有意义:数据只在 ingest 后变化,
// 而后端已按 table.version 缓存了派生结果,网络往返仍是纯开销。
// 这里保留最近一次成功结果:再次进入先用旧值立即渲染,同时后台刷新覆盖。
// 只用于"可容忍短暂陈旧"的只读列表;检索/读页等强时效请求不走缓存。
const swr = new Map<string, { at: number; value: unknown }>()
const SWR_TTL_MS = 5 * 60 * 1000

/**
 * 先交付缓存的旧值(若有),再后台刷新并回调新值。
 * 无缓存时等待请求完成;TTL 内且已有缓存则不再发请求。
 */
export function getSWR<T>(
  key: string,
  fetcher: () => Promise<T>,
  onFresh: (v: T) => void,
): Promise<void> {
  const hit = swr.get(key)
  if (hit) {
    onFresh(hit.value as T)                       // 先给旧值,页面立即可用
    if (Date.now() - hit.at < SWR_TTL_MS) return Promise.resolve()
  }
  return fetcher().then((v) => {
    swr.set(key, { at: Date.now(), value: v })
    onFresh(v)
  })
}

/** 手动失效(ingest 完成、主动刷新时用) */
export function invalidateSWR(prefix = '') {
  for (const k of [...swr.keys()]) if (k.startsWith(prefix)) swr.delete(k)
}
export const searchDocs = (
  q: string, category?: string, topK = 5, mode = 'mixed', rerank = true,
  file?: string, maxPerDoc = 0, signal?: AbortSignal,
) => {
  const params = new URLSearchParams({ q, top_k: String(topK), mode, rerank: String(rerank) })
  if (category) params.set('category', category)
  if (file) params.set('file', file)
  if (maxPerDoc > 0) params.set('max_per_doc', String(maxPerDoc))
  return get<SearchHit[]>('/search?' + params.toString(), signal)
}
export const readPage = (file: string, page: number, signal?: AbortSignal) =>
  get<{ text: string; ocr: boolean; error?: string }>(
    '/page?' + new URLSearchParams({ file, page: String(page) }), signal,
  )
export const runIngest = (rebuild = false) =>
  post<{ ok: boolean; error?: string }>('/ingest' + (rebuild ? '?rebuild=true' : ''))
/** PDF 深链:#page=N 让浏览器查看器直接定位到命中页;MD 无此语义,忽略 page */
export const pdfUrl = (file: string, page?: number) =>
  '/api/pdf?' + new URLSearchParams({ file: file as string }).toString()
  + (page && page > 1 && !/\.(md|markdown)$/i.test(file) ? `#page=${page}` : '')

/** 文档类型:按扩展名区分 md / pdf(后端也返回 kind,这里用于无 kind 时兜底) */
export const docKind = (file: string, kind?: string): 'md' | 'pdf' =>
  kind === 'md' || kind === 'pdf'
    ? kind
    : /\.(md|markdown)$/i.test(file)
      ? 'md'
      : 'pdf'

/** 文档类型标签,用于按钮/角标文案 */
export const docLabel = (file: string, kind?: string) =>
  docKind(file, kind) === 'md' ? 'MD' : 'PDF'

/** 重新提取指定文档(含低文本页的 OCR 兜底) */
export const reingestFiles = (files: string[]) =>
  post<{ ok: boolean; count?: number; error?: string }>('/ingest/files', { files })

/** 逐文档提取质量体检 */
export const getExtractReport = (limit = 200) =>
  get<ExtractReportItem[]>(`/extract/report?limit=${limit}`)

/** 本地 OCR 服务状态 */
export const getOcrHealth = () => get<OcrHealth>('/ocr/health')

export const getConfig = () => get<ConfigPayload>('/config')
export const saveConfig = (values: Record<string, unknown>) =>
  put<{ ok: boolean; specs: Record<string, ConfigSpec> }>('/config', { values })
export const resetConfig = (names?: string[]) =>
  post<{ ok: boolean; specs: Record<string, ConfigSpec> }>('/config/reset',
    names ? { names } : {})

// ---------- 导出 / 导入 ----------

/** 数据包清单摘要 */
export interface BundleManifest {
  format: string
  version: number
  created_at: string
  includes_documents?: boolean
  counts: { documents: number; chunks: number }
  embedding: { base_url: string; model: string; dim: number | null }
  source?: { pdf_root: string; db_path: string }
  documents?: { file: string; md5: string; pages: number }[]
}

export interface BundleEntry {
  name: string
  bytes: number
  mtime: string
  manifest: BundleManifest | null
  error?: string
}

export interface ProviderDiff {
  bundle: Record<string, string>
  current: Record<string, string>
  /** 包内与当前不一致的项 */
  changed: Record<string, { bundle: string; current: string }>
}

export interface InspectResult {
  name: string
  manifest: BundleManifest
  /** 包内嵌入服务与当前的差异(数据与模型强绑定,导入可一并应用) */
  provider: ProviderDiff
  /** 勾选「应用包内服务配置」时的阻断原因;空串表示可导入 */
  blocking_if_apply: string
  /** 保留本地服务配置时的阻断原因(模型不一致会不可用) */
  blocking_if_keep: string
}

export interface ImportResult {
  ok: boolean
  documents_written?: number
  documents_skipped?: number
  index_replaced?: boolean
  index_backup?: string | null
  /** 实际写入的嵌入服务配置 */
  provider_applied?: Record<string, string>
  elapsed?: number
  manifest?: BundleManifest
  error?: string
}

export const configExportUrl = () => `${BASE}/export/config`

/** 把本地配置 JSON 推给后端应用 */
export const importConfig = (payload: unknown) =>
  post<{ ok: boolean; specs: Record<string, ConfigSpec> }>('/import/config', payload)

export const listBundles = () => get<BundleEntry[]>('/export/bundles')
export const buildBundle = (includeDocs: boolean, level: number) =>
  post<{ path: string; bytes: number; documents: number; elapsed: number }>(
    `/export/bundle?include_docs=${includeDocs}&level=${level}`)
export const deleteBundle = (name: string) =>
  del<{ ok: boolean }>(`/export/bundle?name=${encodeURIComponent(name)}`)
export const bundleDownloadUrl = (name: string) =>
  `${BASE}/export/download?name=${encodeURIComponent(name)}`

export const inspectBundle = (name: string) =>
  post<InspectResult>('/import/inspect', { name })
export const applyBundle = (
  name: string, restoreDocs: boolean, replaceIndex: boolean, applyProvider: boolean,
) => post<ImportResult>('/import/bundle', {
  name, restore_docs: restoreDocs, replace_index: replaceIndex, apply_provider: applyProvider,
})
