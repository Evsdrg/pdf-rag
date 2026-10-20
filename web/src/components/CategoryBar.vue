<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  items: { name: string; chunks: number }[]
}>()

const max = computed(() => Math.max(1, ...props.items.map((i) => i.chunks)))
const total = computed(() => props.items.reduce((s, i) => s + i.chunks, 0))
</script>

<template>
  <div class="cat-list">
    <div v-for="c in items" :key="c.name" class="cat">
      <span class="name" :title="c.name">{{ c.name }}</span>
      <div class="track">
        <div class="fill" :style="{ width: (c.chunks / max) * 100 + '%' }" />
      </div>
      <span class="n">{{ c.chunks }}</span>
      <span class="pct">{{ total ? Math.round((c.chunks / total) * 100) : 0 }}%</span>
    </div>
  </div>
</template>

<style scoped>
.cat-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cat {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.name {
  width: 150px;
  color: #a6adc8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.track {
  flex: 1;
  height: 12px;
  background: #313244;
  border-radius: 6px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, #89b4fa, #a6e3a1);
  border-radius: 6px;
  transition: width 0.4s;
}
.n {
  width: 52px;
  text-align: right;
  color: #f9e2af;
  font-variant-numeric: tabular-nums;
}
.pct {
  width: 44px;
  text-align: right;
  color: #6c7086;
  font-variant-numeric: tabular-nums;
}
</style>
