<script setup lang="ts">
import { computed, onMounted, ref, shallowRef } from 'vue'
import {
  NCard, NInput, NSelect, NButton, NTag, NSpace, NEmpty, NSpin, NSwitch, NDivider,
} from 'naive-ui'
import type { SelectOption } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { docLabel, getCategories, searchDocs, pdfUrl } from '../api'
import type { SearchHit, SearchResponse } from '../api'
import PageDrawer from '../components/PageDrawer.vue'
import StructuredEvidence from '../components/StructuredEvidence.vue'

const message = useMessage()
const q = ref('')
const categories = ref<SelectOption[]>([])
const category = ref<string | null>(null)
const results = ref<SearchHit[]>([])
const searching = ref(false)
const searched = ref(false)
const diagnostics = ref('')
const timingSummary = ref('')
const mode = ref('mixed')
const rerank = ref(true)
const structured = shallowRef(false)
const topK = ref(8)
const fileFilter = ref('')
const history = ref<string[]>(JSON.parse(localStorage.getItem('search_history') || '[]'))

/** 读页抽屉的目标(翻页/加载由 PageDrawer 自己负责) */
const viewer = ref<{ file: string; page: number } | null>(null)

/** 在途检索请求:新查询发出前取消旧的,避免慢响应晚到覆盖新结果 */
let inFlight: AbortController | null = null

const drawerShow = computed({
  get: () => !!viewer.value,
  set: (v: boolean) => {
    if (!v) viewer.value = null
  },
})

onMounted(async () => {
  try {
    const cats = await getCategories()
    categories.value = cats.map((c) => ({ label: c, value: c }))
  } catch {
    message.warning('无法获取类别列表')
  }
})

function formatMs(value: number | undefined) {
  return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)} ms` : ''
}

function timingLabel(response: SearchResponse) {
  const timings = response.timings_ms ?? {}
  const upstream = response.upstream ?? { embedding_cache_hits: 0, embedding_cache_misses: 0 }
  const parts = [`总计 ${formatMs(timings.total) || '—'}`]
  if (response.cached) {
    parts.push('结果缓存命中')
  } else {
    const local = [
      ['FTS', timings.fts], ['型号', timings.substring], ['向量通道', timings.vector],
      ['结构化', timings.structured], ['本地整理', timings.candidate_finalize],
      ['结果组装', timings.result_render],
    ].filter((item): item is [string, number] => typeof item[1] === 'number')
    if (local.length) parts.push(local.map(([name, ms]) => `${name} ${formatMs(ms)}`).join(' · '))
    if (upstream.embeddings) {
      const item = upstream.embeddings
      parts.push(`嵌入 ${formatMs(item.elapsed_ms)}${item.retries ? `（重试 ${item.retries}）` : ''}`)
    }
    if (upstream.rerank) {
      const item = upstream.rerank
      parts.push(`重排 ${formatMs(item.elapsed_ms)}${item.retries ? `（重试 ${item.retries}）` : ''}`)
    }
    if (upstream.embedding_cache_hits || upstream.embedding_cache_misses) {
      parts.push(`向量缓存 ${upstream.embedding_cache_hits} 命中 / ${upstream.embedding_cache_misses} 未命中`)
    }
  }
  return parts.join('；')
}

const timingFootnote = '阶段时间彼此包含且不完全可加总；向量缓存只省嵌入调用，未缓存时仍可能执行向量检索和重排。'

function pushHistory(query: string) {
  const h = [query, ...history.value.filter((x) => x !== query)].slice(0, 10)
  history.value = h
  localStorage.setItem('search_history', JSON.stringify(h))
}

async function run(query?: string) {
  const queryText = (query ?? q.value).trim()
  if (!queryText) {
    message.warning('请输入查询内容')
    return
  }
  q.value = queryText
  searching.value = true
  timingSummary.value = ''
  inFlight?.abort()
  const ctrl = new AbortController()
  inFlight = ctrl
  try {
    const response = await searchDocs(
      queryText, category.value || undefined, topK.value, mode.value, rerank.value,
      fileFilter.value.trim() || undefined, 0, ctrl.signal, structured.value,
    )
    results.value = response.results
    timingSummary.value = timingLabel(response)
    const structuredStatus = response.structured
    const statusLabels = {
      disabled: '未启用', skipped: '未识别可连接实体', empty: '无匹配候选', used: '已参与召回', failed: '已降级',
    }
    diagnostics.value = [...new Set([
      response.notice,
      structuredStatus.enabled
        ? `结构化扩展（实验）：${statusLabels[structuredStatus.status]}`
          + (structuredStatus.status === 'used' ? `，补充 ${structuredStatus.added_pages ?? 0} 页候选` : '')
        : '',
      ...response.warnings.map((item) => item.message),
      response.truncated ? response.continuation_hint : '',
    ].filter(Boolean))].join('；')
    searched.value = true
    if (results.value.length) pushHistory(queryText)
  } catch (e) {
    // 主动取消(用户又发起了新查询)不打扰用户
    if ((e as Error).name === 'AbortError') return
    message.error(`查询失败:${(e as Error).message}`)
  } finally {
    if (inFlight === ctrl) {
      searching.value = false
      inFlight = null
    }
  }
}

/** 打开读页抽屉(内容加载与翻页交给 PageDrawer) */
function openPage(hit: SearchHit) {
  viewer.value = { file: hit.file, page: hit.page }
}

function fileBase(file: string) {
  const seg = file.split(/[\\/]/)
  return seg[seg.length - 1]
}
</script>

<template>
  <n-card title="检索测试">
    <n-space vertical :size="12">
      <div class="row">
        <n-input
          v-model:value="q"
          size="large"
          placeholder="输入查询,如: W25Q32 供电电压 / SPI Flash 引脚定义"
          clearable
          @keyup.enter="run()"
        />
      </div>
      <div class="row">
        <n-space align="center" wrap>
          <n-select
            v-model:value="category"
            :options="categories"
            placeholder="全部类别"
            clearable
            style="width: 220px"
          />
          <n-input
            v-model:value="fileFilter"
            size="small"
            placeholder="限定文档:文件名含,如 QMC6309"
            clearable
            style="width: 200px"
          />
          <n-button type="primary" :loading="searching" @click="run()">搜索</n-button>
          <n-divider vertical style="height: 24px" />
          <span class="opt-lbl">条数</span>
          <n-select v-model:value="topK" style="width: 90px" :options="[
            { label: '3', value: 3 },
            { label: '5', value: 5 },
            { label: '8', value: 8 },
            { label: '12', value: 12 },
            { label: '20', value: 20 },
          ]" />
          <span class="opt-lbl">模式</span>
          <n-select v-model:value="mode" style="width: 130px" :options="[
            { label: '混合 (BM25+向量)', value: 'mixed' },
            { label: '仅全文 BM25', value: 'fts' },
            { label: '仅语义向量', value: 'vector' },
          ]" />
          <span class="opt-lbl">重排</span>
          <n-switch v-model:value="rerank" />
          <span class="opt-lbl">结构化扩展（实验）</span>
          <n-switch v-model:value="structured" aria-label="结构化扩展（实验）" />
        </n-space>
      </div>

      <template v-if="history.length">
        <n-space size="small" wrap>
          <span class="opt-lbl">历史:</span>
          <n-tag v-for="h in history" :key="h" size="small" style="cursor: pointer" @click="run(h)">
            {{ h }}
          </n-tag>
        </n-space>
        <n-divider style="margin: 4px 0" />
      </template>

      <p v-if="diagnostics" class="diagnostics" role="status">{{ diagnostics }}</p>
      <p v-if="timingSummary" class="timing-summary" :title="timingFootnote" aria-live="polite">
        检索耗时：{{ timingSummary }}<span class="timing-note">{{ timingFootnote }}</span>
      </p>
      <n-spin :show="searching">
        <div v-if="!searched" class="hint">
          <n-empty description="输入查询并搜索,将混合 BM25 全文 + 语义向量检索" />
        </div>
        <template v-else>
          <div v-if="!results.length" class="hint">
            <n-empty description="无命中结果" />
          </div>
          <div v-else class="results">
            <n-card
              v-for="(r, i) in results"
              :key="i"
              size="small"
              class="hit"
              @click="openPage(r)"
            >
              <template #header>
                <div class="hit-head">
                  <n-space align="center" size="small">
                    <n-tag size="small" type="info">{{ r.score }}</n-tag>
                    <n-tag v-if="r.category" size="small" type="default">{{ r.category }}</n-tag>
                    <n-tag v-if="r.model_no" size="small" type="success">{{ r.model_no }}</n-tag>
                    <n-tag v-else-if="r.product" size="small" type="success">{{ r.product }}</n-tag>
                    <n-tag v-if="r.version" size="small" type="warning">v{{ r.version }}</n-tag>
                  </n-space>
                  <n-space align="center" size="small">
                    <span class="loc">第 {{ r.page }} 页</span>
                    <n-button size="tiny" tag="a" :href="pdfUrl(r.file, r.page)" target="_blank" @click.stop>
                      {{ docLabel(r.file, r.kind) }}
                    </n-button>
                  </n-space>
                </div>
              </template>
              <div class="fname">{{ fileBase(r.file) }}</div>
              <div class="fpath">{{ r.file }}</div>
              <div class="snippet">{{ r.snippet }}</div>
              <StructuredEvidence :hit="r" />
            </n-card>
          </div>
        </template>
      </n-spin>
    </n-space>
  </n-card>

  <PageDrawer v-model:show="drawerShow" :file="viewer?.file ?? ''" :page="viewer?.page ?? 1" :width="760" />
</template>

<style scoped>
.diagnostics { color: #f9e2af; margin: 0; font-size: 13px; }
.timing-summary { color: #a6adc8; margin: -6px 0 0; font-size: 12px; line-height: 1.5; }
.timing-note { display: block; color: #7f849c; font-size: 11px; }
.row {
  max-width: 760px;
}
.opt-lbl {
  font-size: 13px;
  color: #6c7086;
}
.results {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 900px;
}
.hit {
  cursor: pointer;
  transition: border-color 0.2s;
}
.hit:hover {
  border-color: #89b4fa;
}
.hit-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.loc {
  font-size: 12px;
  color: #6c7086;
}
.fname {
  font-weight: 600;
  color: #cdd6f4;
  font-size: 13px;
}
.fpath {
  font-family: Consolas, monospace;
  font-size: 11px;
  color: #6c7086;
  margin: 2px 0 8px;
  word-break: break-all;
}
.snippet {
  font-size: 13px;
  color: #a6adc8;
  white-space: pre-wrap;
  line-height: 1.6;
  max-height: 160px;
  overflow: auto;
}
.hint {
  padding: 40px 0;
}
</style>
