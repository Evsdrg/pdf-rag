<script setup lang="ts">
/**
 * 读页抽屉:显示某一页的提取文本,支持翻页与「打开原文」。
 *
 * SearchView / FileListView 各有一份几乎逐字的实现(只有宽度和 OCR 标签文案不同),
 * 收进这里避免两处漂移。翻页时组件自己请求页面,父组件只负责开关。
 */
import { computed, shallowRef, watch } from 'vue'
import { NButton, NDrawer, NDrawerContent, NSpace, NTag } from 'naive-ui'
import { pdfUrl, readPage } from '../api'

const props = withDefaults(defineProps<{
  show: boolean
  file?: string
  page?: number
  /** 抽屉宽度(px) */
  width?: number
  /** OCR 标签文案(两个页面措辞曾不一致,统一在此控制) */
  ocrLabel?: string
}>(), {
  file: '',
  page: 1,
  width: 740,
  ocrLabel: 'OCR 识别',
})

const emit = defineEmits<{ 'update:show': [boolean] }>()

const visible = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const current = shallowRef(props.page)
const text = shallowRef('')
const isOcr = shallowRef(false)
const loading = shallowRef(false)
const err = shallowRef('')
const warning = shallowRef('')
const cursor = shallowRef<string | null>(null)
const totalPages = shallowRef(0)
let inFlight: AbortController | null = null

async function load(file: string, page: number, append = false) {
  if (!file || page < 1) return
  inFlight?.abort()
  const controller = new AbortController()
  inFlight = controller
  loading.value = true
  err.value = ''
  if (!append) {
    text.value = ''
    warning.value = ''
    cursor.value = null
  }
  try {
    const response = await readPage(file, page, controller.signal, append ? cursor.value ?? '' : '')
    if (inFlight !== controller) return
    text.value = append ? text.value + response.text : response.text || '(空)'
    isOcr.value = response.ocr
    warning.value = response.warnings.map((item) => item.message).join('；')
    totalPages.value = response.total_pages
    cursor.value = response.next_cursor
  } catch (e) {
    if ((e as Error).name !== 'AbortError') err.value = `读取失败:${(e as Error).message}`
  } finally {
    if (inFlight === controller) {
      loading.value = false
      inFlight = null
    }
  }
}

// 外部指定了新文件/新页 → 同步页码
watch(
  () => [props.file, props.page] as const,
  ([, p]) => { current.value = p },
  { immediate: true },
)

// 每次打开都按 props.page 重新加载。
// 不能用"无内容才加载"判断:text 是组件级状态,上一次翻到第 N 页后会残留,
// 再次打开新文档时会跳过加载、显示上一份文档的内容(实测踩到)。
watch(visible, (v) => {
  if (v) {
    current.value = props.page
    load(props.file, props.page)
  } else {
    inFlight?.abort()
    inFlight = null
    loading.value = false
  }
})

function turn(delta: number) {
  const p = current.value + delta
  if (p < 1) return
  current.value = p
  load(props.file, p)
}
</script>

<template>
  <n-drawer v-model:show="visible" :width="width" placement="right">
    <n-drawer-content v-if="file" closable :title="`${file} 第${current}页`">
      <n-space class="page-nav" align="center">
        <n-button size="small" :disabled="current <= 1" :loading="loading" @click="turn(-1)">上一页</n-button>
        <span>第 {{ current }} 页</span>
        <n-button size="small" :disabled="loading || (totalPages > 0 && current >= totalPages)" :loading="loading" @click="turn(1)">下一页</n-button>
        <n-tag v-if="isOcr" size="small" type="warning" round>{{ ocrLabel }}</n-tag>
        <n-button size="small" tag="a" :href="pdfUrl(file, current)" target="_blank">打开原文</n-button>
      </n-space>
      <p v-if="warning" class="page-warning" role="status">{{ warning }}</p>
      <pre class="page-text">{{ err || text }}</pre>
      <n-button v-if="cursor" size="small" :loading="loading" @click="load(file, current, true)">继续读取本页</n-button>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.page-nav { margin-bottom: 12px; }
.page-warning { color: #f9e2af; font-size: 13px; }
.page-text {
  white-space: pre-wrap;
  font-family: Consolas, monospace;
  font-size: 12.5px;
  line-height: 1.7;
  color: #cdd6f4;
  max-height: 75vh;
  overflow: auto;
}
</style>
