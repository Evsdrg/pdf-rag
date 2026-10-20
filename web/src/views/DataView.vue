<script setup lang="ts">
/**
 * 数据管理:配置文件导出/导入,以及"向量索引 + 手册"数据包的构建、下载与导入。
 *
 * 大包(含手册可达数百 MB)走"先在后端构建到磁盘、再下载"的两步流程:
 * 同步返回大响应体容易超时,而且重复下载不该重复构建。
 */
import { computed, h, onMounted, ref } from 'vue'
import {
  NAlert, NButton, NCard, NDataTable, NInputNumber, NPopconfirm, NSpace,
  NSpin, NSwitch, NTag, useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  applyBundle, buildBundle, bundleDownloadUrl, configExportUrl, deleteBundle,
  importConfig, inspectBundle, listBundles,
  type BundleEntry, type InspectResult,
} from '../api'

const message = useMessage()
const loading = ref(true)
const building = ref(false)
const importing = ref(false)
const bundles = ref<BundleEntry[]>([])

// 构建参数
const includeDocs = ref(true)
const level = ref(6)

// 导入状态
const inspected = ref<InspectResult | null>(null)
const restoreDocs = ref(true)
const replaceIndex = ref(true)
/** 数据与模型强绑定:默认应用包内嵌入服务配置,否则模型不一致时向量不可比 */
const applyProvider = ref(true)

const buildHint = computed(() =>
  includeDocs.value
    ? '包含向量索引与全部对应 PDF,可在另一台机器完整复原'
    : '只包含向量索引(需目标机已有同样的 PDF 才能检索到正文)',
)

async function load() {
  loading.value = true
  try {
    bundles.value = await listBundles()
  } catch (e) {
    message.error(`读取数据包列表失败:${(e as Error).message}`)
  } finally {
    loading.value = false
  }
}

async function build() {
  building.value = true
  try {
    const r = await buildBundle(includeDocs.value, level.value)
    message.success(`已构建 ${(r.bytes / 1048576).toFixed(0)} MB,耗时 ${r.elapsed}s`)
    await load()
  } catch (e) {
    message.error(`构建失败:${(e as Error).message}`)
  } finally {
    building.value = false
  }
}

async function inspect(name: string) {
  try {
    inspected.value = await inspectBundle(name)
  } catch (e) {
    message.error(`预检失败:${(e as Error).message}`)
  }
}

/** 当前开关下的阻断原因(切换"应用包内服务配置"会改变结论) */
const blocking = computed(() => {
  const t = inspected.value
  if (!t) return ''
  return applyProvider.value ? t.blocking_if_apply : t.blocking_if_keep
})

const changedProviders = computed(() =>
  Object.entries(inspected.value?.provider?.changed ?? {}),
)

async function doImport() {
  const target = inspected.value
  if (!target) return
  importing.value = true
  try {
    const r = await applyBundle(target.name, restoreDocs.value, replaceIndex.value, applyProvider.value)
    message.success(
      `导入完成:PDF 新增 ${r.documents_written}、跳过 ${r.documents_skipped}` +
      (r.index_replaced ? `,索引已替换(备份 ${r.index_backup ?? '无'})` : '') +
      (r.provider_applied && Object.keys(r.provider_applied).length
        ? `,已应用包内服务配置(${Object.keys(r.provider_applied).join('、')})` : ''),
    )
    inspected.value = null
  } catch (e) {
    message.error(`导入失败:${(e as Error).message}`)
  } finally {
    importing.value = false
  }
}

async function remove(name: string) {
  try {
    await deleteBundle(name)
    message.success('已删除')
    await load()
  } catch (e) {
    message.error(`删除失败:${(e as Error).message}`)
  }
}

/** 导入配置文件:用隐藏 file input 读本地 JSON 再推给后端 */
const fileInput = ref<HTMLInputElement | null>(null)

function pickConfig() {
  fileInput.value?.click()
}

async function onConfigPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    const payload = JSON.parse(await file.text())
    const r = await importConfig(payload)
    const n = Object.keys(r.specs ?? {}).length
    message.success(`配置已导入并生效(${n} 项)`)
  } catch (err) {
    message.error(`导入配置失败:${(err as Error).message}`)
  }
}

function mb(bytes: number) {
  return `${(bytes / 1048576).toFixed(1)} MB`
}

onMounted(load)

const columns = computed<DataTableColumns<BundleEntry>>(() => [
  { title: '包名', key: 'name', ellipsis: { tooltip: true } },
  { title: '大小', key: 'bytes', width: 100, render: (r) => mb(r.bytes) },
  {
    title: '内容', key: 'content', width: 190,
    render: (r) => {
      const m = r.manifest
      if (!m) return h(NTag, { size: 'small', type: 'error' }, () => '清单不可读')
      return h(NSpace, { size: 4 }, () => [
        h(NTag, { size: 'small' }, () => `${m.counts.documents} 文档`),
        h(NTag, { size: 'small' }, () => `${m.counts.chunks} 块`),
        m.includes_documents
          ? h(NTag, { size: 'small', type: 'success' }, () => '含 PDF')
          : h(NTag, { size: 'small', type: 'warning' }, () => '仅索引'),
      ])
    },
  },
  {
    title: '嵌入模型', key: 'model', width: 170,
    render: (r) => r.manifest
      ? h('span', { class: 'muted' }, `${r.manifest.embedding.model} / ${r.manifest.embedding.dim ?? '?'}d`)
      : '—',
  },
  { title: '构建时间', key: 'mtime', width: 165, render: (r) => r.mtime.replace('T', ' ') },
  {
    title: '操作', key: 'ops', width: 210,
    render: (r) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', tag: 'a', href: bundleDownloadUrl(r.name) }, () => '下载'),
        h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => inspect(r.name) }, () => '导入'),
        h(NPopconfirm, { onPositiveClick: () => remove(r.name) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error', quaternary: true }, () => '删除'),
          default: () => '确定删除这个数据包?',
        }),
      ]),
  },
])
</script>

<template>
  <div class="page">
    <n-card title="配置导出 / 导入" class="card">
      <div class="hint">
        导出内容为检索可调参数与部署项(根目录、模型名等),<b>不含任何密钥</b>。
      </div>
      <n-space style="margin-top: 12px">
        <n-button tag="a" :href="configExportUrl()" type="primary" secondary>导出配置</n-button>
        <n-button @click="pickConfig">导入配置</n-button>
        <input ref="fileInput" type="file" accept="application/json,.json" hidden @change="onConfigPicked" />
      </n-space>
    </n-card>

    <n-card title="数据包(向量索引 + 手册)" class="card">
      <div class="hint">用 zstd 压缩为单个 <code>.tar.zst</code>,可在另一台机器完整复原检索能力。</div>
      <n-space align="center" style="margin-top: 12px" :size="16">
        <n-space align="center" :size="6">
          <n-switch v-model:value="includeDocs" size="small" />
          <span class="label">包含 PDF 手册</span>
        </n-space>
        <n-space align="center" :size="6">
          <span class="label">压缩级别</span>
          <n-input-number v-model:value="level" size="small" :min="1" :max="19" style="width: 110px" />
        </n-space>
        <n-button type="primary" :loading="building" @click="build">构建数据包</n-button>
      </n-space>
      <div class="hint small">{{ buildHint }}</div>
    </n-card>

    <n-card title="已有数据包" class="card">
      <n-spin :show="loading">
        <n-data-table
          v-if="bundles.length"
          :columns="columns"
          :data="bundles"
          size="small"
          :bordered="false"
          :scroll-x="1000"
        />
        <div v-else class="hint">还没有数据包,先在上方构建一个。</div>
      </n-spin>
    </n-card>

    <n-card v-if="inspected" title="导入预检" class="card">
      <n-alert v-if="blocking" type="error" style="margin-bottom: 12px">{{ blocking }}</n-alert>
      <n-alert v-else type="success" style="margin-bottom: 12px">可以导入。</n-alert>

      <div class="grid">
        <div><span class="k">包名</span>{{ inspected.name }}</div>
        <div><span class="k">创建时间</span>{{ inspected.manifest.created_at }}</div>
        <div><span class="k">文档 / 块</span>{{ inspected.manifest.counts.documents }} / {{ inspected.manifest.counts.chunks }}</div>
        <div><span class="k">嵌入模型</span>{{ inspected.manifest.embedding.model }} / {{ inspected.manifest.embedding.dim ?? '?' }} 维</div>
        <div><span class="k">源语料库</span>{{ inspected.manifest.source?.pdf_root ?? '—' }}</div>
      </div>

      <div class="provider">
        <div class="ptitle">嵌入服务(数据与模型强绑定)</div>
        <div v-if="!changedProviders.length" class="hint small">
          与当前配置一致:{{ inspected.provider.current.embed_model }}
        </div>
        <table v-else class="ptable">
          <thead><tr><th>项</th><th>包内</th><th>当前</th></tr></thead>
          <tbody>
            <tr v-for="[k, v] in changedProviders" :key="k">
              <td>{{ k }}</td><td class="bundle">{{ v.bundle }}</td><td class="cur">{{ v.current }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <n-space align="center" style="margin-top: 14px" :size="18">
        <n-space align="center" :size="6">
          <n-switch v-model:value="restoreDocs" size="small" />
          <span class="label">还原 PDF(已存在且 md5 相同则跳过)</span>
        </n-space>
        <n-space align="center" :size="6">
          <n-switch v-model:value="replaceIndex" size="small" />
          <span class="label">替换索引</span>
        </n-space>
        <n-space align="center" :size="6">
          <n-switch v-model:value="applyProvider" size="small" />
          <span class="label">应用包内服务配置</span>
        </n-space>
      </n-space>

      <n-alert type="warning" class="gap">
        替换索引会先自动备份现有索引到 <code>index.lance.bak-&lt;时间戳&gt;</code>;
        导入后若需回退,把备份目录改回 <code>index.lance</code> 即可。
      </n-alert>
      <n-alert v-if="applyProvider && changedProviders.length" type="warning" class="gap">
        将把嵌入服务切换为包内配置。请确认本地 <code>EMBED_API_KEY</code> 对该服务有效 ——
        密钥只从本地环境读取,不会随包携带。
      </n-alert>

      <n-space style="margin-top: 12px">
        <n-button type="primary" :loading="importing" :disabled="!!blocking" @click="doImport">
          执行导入
        </n-button>
        <n-button @click="inspected = null">取消</n-button>
      </n-space>
    </n-card>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; }
.card { margin-bottom: 16px; }
.hint { font-size: 12.5px; color: #a6adc8; line-height: 1.6; }
.hint.small { font-size: 12px; color: #6c7086; margin-top: 10px; }
.hint code { color: #89b4fa; }
.label { font-size: 13px; color: #cdd6f4; }
.muted { color: #6c7086; font-size: 12.5px; }
.gap { margin: 12px 0; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 6px 20px;
  font-size: 13px;
  color: #cdd6f4;
}
.k { display: inline-block; width: 76px; color: #6c7086; }
.provider { margin-top: 14px; }
.ptitle { font-size: 12.5px; color: #a6adc8; margin-bottom: 6px; }
.ptable { border-collapse: collapse; font-size: 12.5px; }
.ptable th, .ptable td { border: 1px solid #313244; padding: 4px 10px; text-align: left; }
.ptable th { color: #6c7086; font-weight: 500; }
.ptable .bundle { color: #89b4fa; }
.ptable .cur { color: #6c7086; }
</style>
