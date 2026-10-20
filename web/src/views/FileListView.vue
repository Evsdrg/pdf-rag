<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import {
  NAlert, NButton, NCard, NDataTable, NEmpty, NInput,
  NSelect, NSpace, NSpin, NSwitch, NTag, NTooltip, useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption } from 'naive-ui'
import PageDrawer from '../components/PageDrawer.vue'
import {
  docLabel, getCategories, getExtractReport, getFiles, getOcrHealth, getSWR, pdfUrl,
  reingestFiles, type ExtractReportItem, type FileEntry, type OcrHealth,
} from '../api'

/** 文件条目 + 提取质量,合成一行展示 */
interface Row extends FileEntry {
  chars_per_page?: number
  suspect?: boolean
}

const message = useMessage()
const files = ref<Row[]>([])
const categories = ref<SelectOption[]>([])
const category = ref<string | null>(null)
const keyword = ref('')
const onlySuspect = ref(false)
const err = ref('')
const loading = ref(true)
const busy = ref(false)
const ocr = ref<OcrHealth | null>(null)
const checked = ref<string[]>([])

/** 读页抽屉的目标(翻页/加载由 PageDrawer 自己负责) */
const viewer = ref<{ file: string; page: number } | null>(null)

const drawerShow = computed({
  get: () => !!viewer.value,
  set: (v: boolean) => {
    if (!v) viewer.value = null
  },
})

onMounted(async () => {
  // 三路并行。SPA 内切回本页时 getSWR 会先用上次结果立即渲染,后台静默刷新。
  // 不自动请求 OCR 健康:那属于主动探测上游,**只在用户点「刷新 OCR 状态」时查**。
  try {
    await Promise.all([
      getSWR('categories', getCategories, (cats) => {
        categories.value = cats.map((c) => ({ label: c, value: c }))
      }),
      load(),
    ])
  } catch (e) {
    err.value = `无法连接后端服务:${(e as Error).message}`
  } finally {
    loading.value = false
  }
})

/**
 * OCR 状态只在用户主动点按钮时拉一次(不自动、不定时)。
 * 后端返回的是"最近一次真实调用的结果",不再探测上游。
 */
async function loadOcr() {
  try {
    ocr.value = await getOcrHealth()
  } catch (e) {
    message.error(`读取 OCR 状态失败:${(e as Error).message}`)
  }
}

async function load() {
  loading.value = true
  try {
    // 体检数据按文件路径对齐到列表;取不到时降级为纯文件列表,不影响其他功能。
    // 两路都用 SWR:切回本页时先出上次结果,后台再刷新。
    await Promise.all([
      getSWR(`files:${category.value ?? ''}`, () => getFiles(category.value || undefined),
        (list) => { files.value = merge(list, lastReport) }),
      getSWR('report', () => getExtractReport(200),
        (report) => {
          lastReport = report
          files.value = merge(files.value as FileEntry[], report)
        }).catch(() => {
          // 体检接口失败时降级为纯文件列表(与改动前行为一致)
          files.value = files.value.map((f) => ({ ...f, chars_per_page: undefined, suspect: undefined }))
        }),
    ])
    checked.value = []
  } finally {
    loading.value = false
  }
}

/** 最近一次的体检数据:文件列表先到时也要能立刻合并上 */
let lastReport: ExtractReportItem[] = []

/** 把体检数据按文件路径并入文件列表 */
function merge(list: FileEntry[], report: ExtractReportItem[]): Row[] {
  const byFile = new Map(report.map((r) => [r.file, r]))
  return list.map((f) => {
    const r = byFile.get(f.file)
    return { ...f, chars_per_page: r?.chars_per_page, suspect: r?.suspect }
  })
}

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  return files.value.filter((f) => {
    if (onlySuspect.value && !f.suspect) return false
    if (!k) return true
    return (
      f.file.toLowerCase().includes(k) ||
      (f.model_no || '').toLowerCase().includes(k) ||
      (f.c_id || '').toLowerCase().includes(k)
    )
  })
})

const suspectCount = computed(() => files.value.filter((f) => f.suspect).length)

/** OCR 状态:后端返回的是"最近一次真实调用"的记录,不再主动探测上游 */
const ocrText = computed(() => {
  if (!ocr.value) return 'OCR 状态未查询'
  const lc = ocr.value.last_call
  const be = ocr.value.backend === 'remote' ? '远程' : '本机'
  if (!lc) return `${be} OCR · 尚无调用记录`
  return lc.ok
    ? `${be} OCR · 上次成功 ${lc.at}`
    : `${be} OCR · 上次失败 ${lc.at}`
})

const ocrTagType = computed<'success' | 'error' | 'default'>(() => {
  const lc = ocr.value?.last_call
  if (!ocr.value || !lc) return 'default'
  return lc.ok ? 'success' : 'error'
})

/** 打开读页抽屉(内容加载与翻页交给 PageDrawer) */
function openViewer(file: string, page: number) {
  viewer.value = { file, page }
}

/** 对勾选的文档重跑提取(含低文本页 OCR 兜底) */
async function reingestSelected() {
  if (!checked.value.length) return
  busy.value = true
  try {
    const r = await reingestFiles(checked.value)
    if (r.ok) {
      message.success(`已开始重新提取 ${r.count} 个文档,进度见「索引状态」`)
      checked.value = []
    } else {
      message.error(r.error || '启动失败')
    }
  } catch (e) {
    message.error(`启动失败:${(e as Error).message}`)
  } finally {
    busy.value = false
  }
}

const columns = computed<DataTableColumns<Row>>(() => [
  { type: 'selection' },
  { title: '类别', key: 'category', width: 120, render: (r) => h(NTag, { size: 'small' }, () => r.category) },
  {
    // 型号为空时(如按系列命名的 Markdown)回退显示派生的产品/系列名
    title: '型号', key: 'model_no', width: 190,
    render: (r) => r.model_no || r.product || '',
  },
  {
    title: '文件', key: 'file', ellipsis: { tooltip: true },
    render: (r) => h('span', {}, [
      h(NTag, { size: 'tiny', type: r.kind === 'md' ? 'info' : 'default', style: 'margin-right:6px' },
        () => docLabel(r.file, r.kind)),
      r.file,
    ]),
  },
  { title: '页数', key: 'pages', width: 64 },
  { title: '块数', key: 'chunks', width: 64 },
  {
    title: '提取密度',
    key: 'chars_per_page',
    width: 130,
    render: (r) => {
      if (r.chars_per_page === undefined) return h('span', { class: 'muted' }, '—')
      const text = `${r.chars_per_page.toFixed(0)} 字符/页`
      return r.suspect
        ? h(NTag, { size: 'small', type: 'error' }, () => text)
        : h('span', { class: 'ok' }, text)
    },
  },
  {
    title: '操作', key: 'ops', width: 150,
    render: (r) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => openViewer(r.file, 1) }, () => '看首页'),
        h(NButton, { size: 'small', tag: 'a', href: pdfUrl(r.file), target: '_blank' }, () => docLabel(r.file, r.kind)),
      ]),
  },
])
</script>

<template>
  <n-card title="文件库">
    <div class="toolbar">
      <n-select
        v-model:value="category"
        :options="categories"
        placeholder="全部类别"
        clearable
        style="width: 200px"
        @update:value="load"
      />
      <n-input v-model:value="keyword" placeholder="筛选:文件名 / 型号 / C编号" clearable style="width: 260px" />
      <div class="flag">
        <n-switch v-model:value="onlySuspect" size="small" />
        <span>只看提取异常</span>
        <n-tag v-if="suspectCount" size="small" type="error" round>{{ suspectCount }}</n-tag>
      </div>
      <span class="count">{{ filtered.length }} 个文件</span>
    </div>

    <div class="toolbar">
      <n-button
        type="primary"
        :loading="busy"
        :disabled="!checked.length"
        @click="reingestSelected"
      >
        重新提取所选({{ checked.length }})
      </n-button>
      <n-button size="small" quaternary @click="loadOcr">刷新 OCR 状态</n-button>
      <n-tooltip trigger="hover">
        <template #trigger>
          <n-tag size="small" :type="ocrTagType" round>{{ ocrText }}</n-tag>
        </template>
        状态来自最近一次真实 OCR 调用,不做主动探测。要看当前是否为最新,点左侧「刷新 OCR 状态」。
      </n-tooltip>
      <span class="muted small">OCR 地址 {{ ocr?.url || '-' }}</span>
    </div>

    <n-alert v-if="suspectCount" type="warning" class="gap">
      有 {{ suspectCount }} 份文档的每页文本量异常偏低(接近只有页眉),在库中基本不可检索。
      勾选后点「重新提取所选」会重跑文本提取并对低文本页调用本地 OCR。
    </n-alert>
    <n-alert v-if="err" type="warning" class="gap">{{ err }}</n-alert>

    <n-spin :show="loading">
      <n-data-table
        v-if="filtered.length"
        v-model:checked-row-keys="checked"
        :columns="columns"
        :data="filtered"
        :row-key="(r: Row) => r.file"
        size="small"
        :bordered="false"
        :scroll-x="1000"
      />
      <n-empty v-else description="无文件" class="gap" />
    </n-spin>
  </n-card>

  <PageDrawer v-model:show="drawerShow" :file="viewer?.file ?? ''" :page="viewer?.page ?? 1" :width="720" ocr-label="OCR 结果" />
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.flag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #a6adc8;
}
.count {
  color: #6c7086;
  font-size: 13px;
}
.muted { color: #6c7086; }
.small { font-size: 12px; }
.ok { color: #a6e3a1; font-size: 12.5px; }
.gap { margin: 12px 0; }
</style>
