import type { ConfigSpec } from '../../api'

export interface SettingsSection {
  id: string
  title: string
  description: string
  hint?: string
  primary: string[]
  advanced: string[]
}

export const sections: SettingsSection[] = [
  {
    id: 'services', title: '服务与模型', description: '接入服务、选择嵌入和重排模型。',
    hint: '嵌入模型、维度和输入类型必须与已有向量分区匹配。切换不会自动重建索引；密钥仍由环境变量提供。',
    primary: ['embed_base_url', 'embed_model', 'embed_dimensions', 'reranker_model'],
    advanced: ['embed_input_type_doc', 'embed_input_type_query', 'vector_models_priority', 'vector_models_exclude', 'vector_coverage_min'],
  },
  {
    id: 'index', title: '索引与并发', description: '调整本地解析、OCR 请求和向量化吞吐。',
    hint: '本地解析进程可同时处理不同文档；OCR 通路为整轮共用，两者不相乘。高性能机器可提高解析并发，OCR 还受服务端算力和限流约束。保存后下一轮索引生效。',
    primary: ['extract_workers', 'ocr_workers', 'embed_workers', 'embed_batch'],
    advanced: ['chunk_max_chars', 'chunk_overlap_chars', 'embed_attempts'],
  },
  {
    id: 'ocr', title: 'OCR 与提取', description: '配置识别后端、低文本页筛选和提取质量。',
    hint: '优先配置后端与内容筛选；提高 DPI 会增加渲染、传输和识别成本。已有文档不会因改配置而自动重新索引。',
    primary: ['ocr_backend', 'ocr_url', 'ocr_api_base', 'ocr_model', 'ocr_smart_filter', 'ocr_min_chars'],
    advanced: ['ocr_timeout', 'ocr_dpi', 'ocr_prompt', 'min_chars_per_page', 'table_min_ratio'],
  },
  {
    id: 'retrieval', title: '检索效果', description: '调整返回片段、候选深度和结果排序。',
    hint: '先改常用项并到“检索测试”复核。融合权重和去重阈值属于高级调参，不建议无对照地批量修改。',
    primary: ['snippet_width', 'max_per_doc', 'rerank_pool_floor', 'cand_floor', 'rerank_on_window', 'rerank_meta'],
    advanced: ['rrf_k', 'substring_bonus_rank', 'cand_mult', 'cand_mult_category', 'rerank_pool_mult',
      'rerank_rank_weight', 'rerank_tie_tolerance', 'window_stride_div', 'num_unit_bonus', 'toc_scan_chars',
      'penalty_cover', 'penalty_toc_rev', 'block_sim_threshold'],
  },
  {
    id: 'performance', title: '性能与连接', description: '设置缓存、接口超时和连接池。',
    primary: ['query_cache_ttl', 'query_cache_size', 'http_timeout', 'http_connect_timeout'],
    advanced: ['embed_cache_size', 'http_keepalive', 'http_max_conn', 'retry_attempts', 'retry_base_delay', 'page_max_chars'],
  },
]

export const commonNames = [
  'extract_workers', 'ocr_workers', 'embed_workers', 'embed_batch',
  'ocr_smart_filter', 'ocr_backend', 'embed_base_url', 'embed_model',
  'reranker_model', 'snippet_width', 'max_per_doc', 'query_cache_ttl',
]

export function sectionOf(name: string): SettingsSection | undefined {
  return sections.find((section) => [...section.primary, ...section.advanced].includes(name))
}

export function matchesSetting(name: string, spec: ConfigSpec, query: string): boolean {
  const section = sectionOf(name)
  const haystack = [name, spec.label, spec.desc, spec.env_key, spec.group, section?.title ?? ''].join(' ').toLowerCase()
  return query.trim().toLowerCase().split(/\s+/).every((word) => haystack.includes(word))
}
