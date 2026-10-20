<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { NCard, NAlert, NTag, NSpace, NSpin, NButton, NPopconfirm, useMessage } from 'naive-ui'
import { getState, runIngest } from '../api'
import type { IngestState } from '../api'
import ProgressBar from '../components/ProgressBar.vue'

const message = useMessage()
const state = ref<IngestState | null>(null)
const err = ref('')
const starting = ref(false)
let timer: number | undefined

async function poll() {
  try {
    state.value = await getState()
    err.value = ''
  } catch (e) {
    err.value = `无法连接后端服务:${(e as Error).message}`
  }
}

/** 运行时 1s 高频轮询;空闲/终态降到 10s —— 页面常开着也不该每天白发 8.6 万个请求 */
const running = computed(() => state.value?.phase === 'extracting' || state.value?.phase === 'indexing')
const FAST_MS = 1000
const SLOW_MS = 10000

function schedule() {
  window.clearInterval(timer)
  timer = window.setInterval(poll, running.value ? FAST_MS : SLOW_MS)
}

onMounted(() => {
  poll().then(schedule)
})
onUnmounted(() => window.clearInterval(timer))

// 阶段一变(开始/结束)即切换频率
watch(running, schedule)

async function start(rebuild: boolean) {
  starting.value = true
  try {
    const r = await runIngest(rebuild)
    if (r.ok) {
      message.success(rebuild ? '全量重建已启动' : '增量索引已启动')
      poll()
    } else {
      message.error(r.error || '启动失败')
    }
  } catch (e) {
    message.error(`无法连接后端:${(e as Error).message}`)
  } finally {
    starting.value = false
  }
}

const exD = computed(() => state.value?.extract?.done ?? 0)
const exT = computed(() => state.value?.extract?.total ?? 0)
const emD = computed(() => state.value?.embed?.done ?? 0)
const emT = computed(() => state.value?.embed?.total ?? 0)
const eta = computed(() => {
  const s = state.value
  if (!s || s.phase === 'done') return '-'
  const cur = s.phase === 'extracting' ? exD.value : emD.value
  const tot = s.phase === 'extracting' ? exT.value : emT.value
  const rate = s.elapsed && s.elapsed > 0 ? cur / s.elapsed : 0
  return rate > 0 ? Math.round((tot - cur) / rate) + 's' : '-'
})
</script>

<template>
  <n-card title="索引进度">
    <template #header-extra>
      <div class="head">
        <n-space align="center">
          <n-tag v-if="running" type="info">运行中</n-tag>
          <n-tag v-else-if="state?.phase === 'done'" type="success">完成</n-tag>
          <n-tag v-else type="default">未运行</n-tag>
        </n-space>
        <n-space align="center" :size="8">
          <n-button size="small" type="primary" :loading="starting" :disabled="running" @click="start(false)">
            增量索引
          </n-button>
          <n-popconfirm @positive-click="start(true)">
            <template #trigger>
              <n-button size="small" type="warning" :loading="starting" :disabled="running">全量重建</n-button>
            </template>
            全量重建会清空索引后重新处理全部 PDF,耗时约 5 分钟,确认?
          </n-popconfirm>
        </n-space>
      </div>
    </template>

    <n-spin :show="!state">
      <div v-if="err" class="err">
        <n-alert type="warning">{{ err }}</n-alert>
      </div>

      <template v-else-if="state">
        <div class="block">
          <div class="row-label"><span>提取 PDF 文本</span></div>
          <ProgressBar :done="exD" :total="exT" color="#89b4fa" />
        </div>
        <div class="block">
          <div class="row-label"><span>向量化写入索引库</span></div>
          <ProgressBar :done="emD" :total="emT" color="#a6e3a1" />
        </div>

        <div class="stats">
          <div class="stat"><b>{{ state.chunks ?? 0 }}</b><span>分块</span></div>
          <div class="stat"><b>{{ state.db_size_mb ?? 0 }} MB</b><span>索引库大小</span></div>
          <div class="stat"><b>{{ state.elapsed }}s</b><span>已耗时</span></div>
          <div class="stat"><b>{{ eta }}</b><span>预计剩余</span></div>
        </div>

        <div class="current" :class="{ dim: !running }">
          {{ running ? (state.current || '准备中...') : (state.finished_at ? '完成时间: ' + state.finished_at : '暂无索引任务') }}
        </div>

        <template v-if="state.errors?.length">
          <n-alert type="error" title="错误" class="gap">
            <div v-for="e in state.errors" :key="e">{{ e }}</div>
          </n-alert>
        </template>
        <template v-if="state.skipped?.length">
          <n-alert type="warning" title="无文本被跳过(扫描件/图片)" class="gap">
            <div v-for="s in state.skipped" :key="s">{{ s }}</div>
          </n-alert>
        </template>
      </template>
    </n-spin>
  </n-card>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  gap: 16px;
}
.phase {
  color: #a6adc8;
  font-size: 13px;
}
.block {
  margin: 18px 0;
}
.row-label {
  margin-bottom: 6px;
  font-size: 13px;
  color: #a6adc8;
}
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 22px 0;
}
.stat {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 8px;
  padding: 10px 14px;
}
.stat b {
  display: block;
  font-size: 20px;
  color: #f9e2af;
}
.stat span {
  font-size: 11px;
  color: #6c7086;
}
.current {
  font-family: Consolas, monospace;
  font-size: 13px;
  color: #a6e3a1;
  word-break: break-all;
  margin: 8px 0;
}
.dim {
  color: #6c7086;
}
.gap {
  margin-top: 16px;
}
</style>
