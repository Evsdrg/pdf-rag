<script setup lang="ts">
import { computed, onMounted, onUnmounted, shallowRef } from 'vue'
import { NAlert, NButton, NCard, NEmpty, NSpace, NSpin, NTag } from 'naive-ui'
import { getLibraryStatus } from '../api'
import type { ApiWarning, LibraryStatus } from '../api'

const status = shallowRef<LibraryStatus | null>(null)
const error = shallowRef('')
const loading = shallowRef(false)
let controller: AbortController | undefined

const health = computed(() => status.value?.health)
const coverage = computed(() => {
  if (!status.value) return 0
  return Math.round(status.value.indexed_files / Math.max(status.value.source_files, 1) * 100)
})
const tone = computed(() => {
  const value = health.value?.status
  if (value === 'ok') return 'success' as const
  if (value === 'degraded') return 'warning' as const
  if (value === 'missing') return 'error' as const
  return 'default' as const
})
const statusLabel = computed(() => ({
  ok: '健康', degraded: '需关注', missing: '索引缺失', unknown: '暂不可用',
}[health.value?.status ?? ''] ?? '未读取'))
const caption = computed(() => {
  if (status.value?.unindexed_files) {
    return `${status.value.unindexed_files} 份新文档待入库`
  }
  if (status.value?.missing_source_files) {
    return `${status.value.missing_source_files} 个索引引用缺少源文件`
  }
  if (health.value?.warnings.length) {
    return '索引可用，存在需要处理的维护项'
  }
  return '文件覆盖完整，索引结构正常'
})
const healthWarnings = computed(() => health.value?.warnings ?? [])
const coverageWarnings = computed<ApiWarning[]>(() => {
  if (!status.value) return []
  const warnings: ApiWarning[] = []
  if (status.value.unindexed_files) {
    warnings.push({
      code: 'UNINDEXED',
      message: `${status.value.unindexed_files} 份源文档尚未索引。请在「索引进度」执行增量索引。`,
    })
  }
  if (status.value.missing_source_files) {
    warnings.push({
      code: 'MISSING_SOURCE',
      message: `${status.value.missing_source_files} 个索引条目缺少源文件。核对源目录后处理失效引用。`,
    })
  }
  return warnings
})

const vectorLabel = computed(() => {
  const partitions = health.value?.vector_partitions
  if (!partitions?.length) return '不可用'
  const ready = partitions.every((part) => part.indices.length > 0)
  return `${partitions.length} 个分区 · ${ready ? '索引就绪' : '有待建索引'}`
})
const snapshotLabel = computed(() => health.value?.entity_snapshot ? '就绪 · 快速启动' : '尚未生成')
const fragmentLabel = computed(() => health.value?.fragmentation_ratio === undefined
  ? '-'
  : `${health.value.fragmentation_ratio.toFixed(2)} ×`)

function bytes(value?: number | null) {
  if (value === undefined || value === null) return '-'
  return value >= 1048576 ? `${(value / 1048576).toFixed(1)} MB` : `${Math.round(value / 1024)} KB`
}
function timestamp(value?: number) {
  return value ? new Date(value * 1000).toLocaleString() : '-'
}

async function refresh() {
  controller?.abort()
  controller = new AbortController()
  loading.value = true
  error.value = ''
  try {
    status.value = await getLibraryStatus(controller.signal)
  } catch (e) {
    if (controller.signal.aborted) return
    error.value = `无法读取索引健康状态：${(e as Error).message}`
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

onMounted(refresh)
onUnmounted(() => controller?.abort())
</script>

<template>
  <n-card class="health-card" title="索引健康">
    <template #header-extra>
      <n-space align="center" :size="8">
        <n-tag :type="tone" size="small">{{ statusLabel }}</n-tag>
        <n-button size="tiny" tertiary :loading="loading" @click="refresh">刷新</n-button>
      </n-space>
    </template>

    <n-spin :show="!status && !error">
      <n-alert v-if="error" type="warning">{{ error }}</n-alert>
      <template v-else-if="status && health">
        <div class="summary">
          <div class="summary-copy">
            <div class="summary-title">{{ caption }}</div>
            <div class="summary-note">基于本地索引、源文件和真实入库记录检查，不探测上游模型。</div>
          </div>
          <div class="coverage" aria-label="源文件索引覆盖率">
            <strong>{{ coverage }}<span>%</span></strong>
            <small>文件覆盖率</small>
          </div>
        </div>

        <div class="metrics">
          <div class="metric">
            <span class="label">源文件 / 已索引</span>
            <strong>{{ status.source_files }} <span class="unit">/ {{ status.indexed_files }}</span></strong>
            <span class="note">{{ status.unindexed_files || 0 }} 份待入库</span>
          </div>
          <div class="metric">
            <span class="label">索引占用</span>
            <strong>{{ bytes(health.disk_bytes) }}</strong>
            <span class="note">数据 {{ bytes(health.data_bytes) }}</span>
          </div>
          <div class="metric">
            <span class="label">存储开销</span>
            <strong :class="{ attention: (health.fragmentation_ratio ?? 0) > 4 }">{{ fragmentLabel }}</strong>
            <span class="note">目录体积 / 真实数据体积</span>
          </div>
          <div class="metric">
            <span class="label">实体快照</span>
            <strong class="small-value">{{ snapshotLabel }}</strong>
            <span class="note" :title="health.entity_snapshot ? timestamp(health.entity_snapshot.mtime) : ''">
              {{ health.entity_snapshot ? `更新于 ${timestamp(health.entity_snapshot.mtime)}` : '首次结构化检索时自动创建' }}
            </span>
          </div>
        </div>

        <div class="services">
          <div class="service">
            <span class="service-name">全文检索</span>
            <span class="service-value" :class="{ bad: !health.fts_index?.length }">
              {{ health.fts_index?.length ? `${health.fts_index.length} 个索引 · 就绪` : '未检测到索引' }}
            </span>
          </div>
          <div class="service">
            <span class="service-name">向量检索</span>
            <span class="service-value">{{ vectorLabel }}</span>
          </div>
          <div class="service">
            <span class="service-name">索引数据</span>
            <span class="service-value">{{ health.rows?.toLocaleString() ?? '-' }} 块 · v{{ health.table_version ?? '-' }}</span>
          </div>
        </div>

        <div v-if="coverageWarnings.length || healthWarnings.length" class="warnings">
          <div v-for="warning in [...coverageWarnings, ...healthWarnings]" :key="warning.code" class="warning-row">
            <span class="warning-mark" aria-hidden="true">!</span>
            <span>{{ warning.message }}</span>
          </div>
        </div>

        <div v-if="health.last_ingest" class="history">
          上次索引：新增 {{ health.last_ingest.added ?? '-' }} · 移除 {{ health.last_ingest.removed ?? '-' }}
          · 跳过 {{ health.last_ingest.skipped }} · 耗时 {{ health.last_ingest.elapsed ?? '-' }}s
        </div>
        <div class="footnote">检查于 {{ status.checked_at }}</div>
      </template>
      <n-empty v-else-if="status && !health" description="当前服务未提供索引健康信息" />
    </n-spin>
  </n-card>
</template>

<style scoped>
.health-card {
  margin-bottom: 20px;
  border-color: #414766;
  background: linear-gradient(115deg, rgba(137, 180, 250, 0.055), rgba(30, 30, 46, 0) 48%);
}
.summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 20px;
}
.summary-copy { min-width: 0; }
.summary-title { color: #e8edf9; font-size: 15px; font-weight: 600; }
.summary-note { margin-top: 5px; color: #7c839f; font-size: 12px; line-height: 1.6; }
.coverage {
  flex: 0 0 auto;
  padding-left: 24px;
  border-left: 1px solid #34394f;
  text-align: right;
}
.coverage strong { display: block; color: #a6e3a1; font-size: 28px; font-weight: 500; line-height: 1; }
.coverage strong span { margin-left: 2px; font-size: 16px; }
.coverage small { display: block; margin-top: 6px; color: #7c839f; font-size: 11px; }
.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1px solid #31364c;
  border-bottom: 1px solid #31364c;
}
.metric {
  min-width: 0;
  padding: 16px 18px;
  border-right: 1px solid #31364c;
}
.metric:first-child { padding-left: 0; }
.metric:last-child { border-right: 0; }
.label { display: block; margin-bottom: 7px; color: #8a92ad; font-size: 12px; }
.metric strong { display: block; overflow: hidden; color: #e2e9f6; font-size: 20px; font-weight: 500; white-space: nowrap; text-overflow: ellipsis; }
.metric strong.small-value { font-size: 15px; line-height: 26px; }
.metric strong.attention { color: #f2cd97; }
.unit { color: #8993aa; font-size: 13px; }
.note { display: block; overflow: hidden; margin-top: 5px; color: #6c748f; font-size: 11px; white-space: nowrap; text-overflow: ellipsis; }
.services { display: flex; flex-wrap: wrap; gap: 10px 26px; padding: 14px 0; }
.service { display: flex; gap: 8px; font-size: 12px; }
.service-name { color: #79829b; }
.service-value { color: #a6e3a1; }
.service-value.bad { color: #f2cd97; }
.warnings { border-left: 2px solid #d6a85d; background: rgba(214, 168, 93, 0.065); }
.warning-row { display: flex; gap: 10px; padding: 8px 12px; color: #d8bd91; font-size: 12px; line-height: 1.65; }
.warning-mark { flex: 0 0 auto; width: 16px; color: #f2cd97; font-weight: 700; }
.history { margin-top: 12px; color: #818ba4; font-size: 11px; }
.footnote { margin-top: 4px; color: #606981; font-size: 11px; }
@media (max-width: 960px) {
  .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .metric:nth-child(2) { border-right: 0; }
  .metric:nth-child(n + 3) { border-top: 1px solid #31364c; }
  .metric:nth-child(3) { padding-left: 0; }
}
@media (max-width: 560px) {
  .summary { align-items: flex-start; gap: 14px; }
  .coverage { padding-left: 14px; }
  .summary-note { max-width: 250px; }
  .metric { padding-right: 10px; }
}
</style>
