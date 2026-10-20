<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NCard, NEmpty, NDataTable, NAlert, NSpin } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getStats, getSWR } from '../api'
import type { Stats, HistoryEntry } from '../api'
import CategoryBar from '../components/CategoryBar.vue'

const stats = ref<Stats | null>(null)
const err = ref('')

onMounted(async () => {
  try {
    // SWR:切回本页时先用上次的统计立即渲染,后台静默刷新
    await getSWR('stats', getStats, (v) => { stats.value = v })
  } catch (e) {
    err.value = `无法连接后端服务:${(e as Error).message}`
  }
})

const histCols: DataTableColumns<HistoryEntry> = [
  { title: '时间', key: 'time' },
  { title: '新增', key: 'added', width: 80 },
  { title: '移除', key: 'removed', width: 80 },
  { title: '分块', key: 'chunks', width: 80 },
  { title: '耗时(s)', key: 'elapsed', width: 90 },
]
</script>

<template>
  <n-spin :show="!stats && !err">
    <div v-if="err">
      <n-alert type="warning">{{ err }}</n-alert>
    </div>
    <template v-else-if="stats">
      <div v-if="!stats.indexed" class="empty">
        <n-empty description="索引库为空,请先在「索引状态」页点击「增量索引」" />
      </div>
      <template v-else>
        <div class="cards">
          <div class="card"><b>{{ stats.files }}</b><span>文档</span></div>
          <div class="card"><b>{{ stats.chunks }}</b><span>总块数</span></div>
          <div class="card"><b>{{ stats.skipped.length }}</b><span>无文本跳过</span></div>
          <div class="card"><b>{{ stats.last_index || '-' }}</b><span>最后索引</span></div>
        </div>

        <div class="grid">
          <n-card title="类别分布" class="col">
            <CategoryBar :items="stats.categories" />
          </n-card>
          <n-card title="索引历史" class="col">
            <n-data-table v-if="stats.history.length" :columns="histCols" :data="stats.history" size="small" :bordered="false" />
            <n-empty v-else description="暂无历史记录" />
          </n-card>
        </div>

        <n-card v-if="stats.skipped.length" title="无文本文件(扫描件,无法索引)" class="gap">
          <div v-for="s in stats.skipped" :key="s" class="skip">{{ s }}</div>
        </n-card>
      </template>
    </template>
  </n-spin>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}
.card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 8px;
  padding: 14px 16px;
}
.card b {
  display: block;
  font-size: 22px;
  color: #f9e2af;
}
.card span {
  font-size: 12px;
  color: #6c7086;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: start;
}
.col {
  min-width: 0;
}
.gap {
  margin-top: 16px;
}
.skip {
  font-family: Consolas, monospace;
  font-size: 12px;
  color: #f9a8a8;
  margin: 4px 0;
}
.empty {
  padding: 60px 0;
}
</style>
