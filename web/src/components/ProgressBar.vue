<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  done: number
  total: number
  color?: string
}>()

const pct = computed(() => (props.total ? Math.round((props.done / props.total) * 100) : 0))
</script>

<template>
  <div class="wrap">
    <div class="bar">
      <div class="fill" :style="{ width: pct + '%', background: color || '#89b4fa' }" />
    </div>
    <span class="lbl">{{ done }} / {{ total }}</span>
  </div>
</template>

<style scoped>
.wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bar {
  flex: 1;
  height: 14px;
  background: #313244;
  border-radius: 7px;
  overflow: hidden;
}
.fill {
  height: 100%;
  border-radius: 7px;
  transition: width 0.4s;
}
.lbl {
  font-size: 13px;
  color: #cdd6f4;
  font-variant-numeric: tabular-nums;
  min-width: 90px;
  text-align: right;
}
</style>
