<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NCard, NEmpty, NDataTable, NAlert, NSpin, NTag, NProgress } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getStats, getSWR } from '../api'
import type { Stats, HistoryEntry, VectorPartition } from '../api'
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

function pct(v: number) { return Math.round(v * 100) }

/** 覆盖率颜色:100% 绿、<100% 黄、0 红 */
function covStatus(v: number): 'success' | 'warning' | 'error' {
  if (v >= 1) return 'success'
  return v > 0 ? 'warning' : 'error'
}

const partCols: DataTableColumns<VectorPartition> = [
  {
    title: '分区', key: 'slug',
    render: (r) => r.slug,
  },
  { title: '模型', key: 'model', render: (r) => r.model || '-' },
  { title: '维度', key: 'dim', width: 70, render: (r) => (r.dim ?? '-') },
  {
    title: '块覆盖', key: 'ratio', width: 150,
    render: (r) => h(NProgress, {
      type: 'line', percentage: pct(r.ratio), status: covStatus(r.ratio),
      height: 8, showIndicator: false,
    }),
  },
  {
    title: '块数', key: 'blocks_covered', width: 130,
    render: (r) => `${r.blocks_covered} / ${r.blocks_total}`,
  },
  {
    title: '文件', key: 'files_covered', width: 110,
    render: (r) => `${r.files_covered} / ${r.files_total}`,
  },
  {
    title: '部分覆盖', key: 'files_partial', width: 100,
    // 有向量块 < 该文件总块数:限流中断或按块补算的痕迹,最容易被忽略
    render: (r) => r.files_partial
      ? h(NTag, { size: 'small', type: 'warning', round: true }, () => `${r.files_partial} 份`)
      : '-',
  },
]

/** 某分区是否参与检索(由后端按优先级/排除算出) */
function isSelected(slug: string) {
  return !!stats.value?.vectors?.selected.includes(slug)
}

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

        <n-card v-if="stats.vectors?.partitions.length" title="向量分区" class="gap">
          <template #header-extra>
            <span class="hint">
              检索使用:{{ stats.vectors.selected.length
                ? stats.vectors.selected.join(' → ')
                : '无(检查优先级/排除配置)' }}
            </span>
          </template>
          <n-data-table :columns="partCols" :data="stats.vectors.partitions"
            size="small" :bordered="false" :row-props="(r: VectorPartition) => ({
              class: isSelected(r.slug) ? 'row-on' : '' })" />
          <div class="hint sub">
            覆盖率按块统计——向量化的输入单位是块,同一文件可能只有部分块有向量。
            「部分覆盖」列显示这类文件数,补跑一次索引可恢复。
          </div>
        </n-card>

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
.hint {
  font-size: 12px;
  color: #6c7086;
}
.hint.sub {
  margin-top: 10px;
  line-height: 1.7;
}
:deep(.row-on td) {
  background: rgba(137, 180, 250, 0.06);
}
.empty {
  padding: 60px 0;
}
</style>
