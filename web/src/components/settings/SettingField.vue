<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NInput, NInputNumber, NSelect, NSwitch, NTag } from 'naive-ui'
import type { ConfigSpec } from '../../api'
import type { SettingValue } from '../../composables/useSettings'

const props = defineProps<{
  name: string
  spec: ConfigSpec
  value: SettingValue
  dirty: boolean
  disabled: boolean
  disabledReason: string
  busy: boolean
  showVariables: boolean
  category?: string
}>()
const emit = defineEmits<{
  change: [value: SettingValue]
  reset: []
}>()

const backendOptions = [
  { label: '本地 OCR 服务', value: 'local' },
  { label: '远程视觉模型', value: 'remote' },
]
const range = computed(() => props.spec.lo !== null || props.spec.hi !== null
  ? `${props.spec.lo ?? '不限'}–${props.spec.hi ?? '不限'}` : '')
const guarded = computed(() => ['embed_model', 'embed_dimensions', 'embed_input_type_doc', 'embed_input_type_query'].includes(props.name))
const nextRun = computed(() => props.spec.group === '索引吞吐' || props.spec.group === '文档提取')
</script>

<template>
  <div class="setting-row" :class="{ dirty, inactive: disabled }">
    <div class="setting-info">
      <div class="setting-title">
        <label :for="`setting-${name}`">{{ spec.label }}</label>
        <NTag v-if="dirty" size="small" type="warning" :bordered="false">未保存</NTag>
        <NTag v-else-if="spec.overridden" size="small" :bordered="false">已自定义</NTag>
        <span v-if="category" class="category-label">{{ category }}</span>
      </div>
      <code v-if="showVariables" class="variable">{{ name }}<template v-if="spec.env_key"> · {{ spec.env_key }}</template></code>
      <div class="description">{{ spec.desc }}</div>
      <div v-if="disabled" class="disabled-reason">{{ disabledReason }}</div>
      <div class="metadata">
        <span>默认：{{ spec.default === '' ? '留空' : spec.default }}</span>
        <span v-if="range">范围：{{ range }}</span>
        <span v-if="guarded" class="risk">须与已有向量匹配</span>
        <span v-else-if="nextRun">下一轮索引生效</span>
      </div>
    </div>
    <div class="setting-control" :class="{ wide: spec.kind === 'str' }">
      <NSwitch v-if="spec.kind === 'bool'" :value="Boolean(value)" :disabled="disabled || busy"
        :aria-label="spec.label" @update:value="emit('change', $event)" />
      <NSelect v-else-if="name === 'ocr_backend'" :value="String(value)" :options="backendOptions"
        :disabled="busy" :input-props="{ id: `setting-${name}`, 'aria-label': spec.label }"
        @update:value="emit('change', $event)" />
      <NInputNumber v-else-if="spec.kind === 'int' || spec.kind === 'float'"
        :value="Number(value)" :min="spec.lo ?? undefined" :max="spec.hi ?? undefined"
        :step="spec.kind === 'int' ? 1 : 0.1" :precision="spec.kind === 'int' ? 0 : 2"
        :disabled="disabled || busy" :input-props="{ id: `setting-${name}`, 'aria-label': spec.label }"
        @update:value="(v: number | null) => v !== null && emit('change', v)" />
      <NInput v-else :value="String(value ?? '')" :disabled="disabled || busy"
        :input-props="{ id: `setting-${name}`, 'aria-label': spec.label }" placeholder="留空使用默认行为"
        @update:value="emit('change', $event)" />
      <NButton v-if="spec.overridden || dirty" text size="small" :disabled="busy" class="reset-button"
        :aria-label="`${dirty ? '撤销该项' : '恢复默认'}：${spec.label}`" @click="emit('reset')">{{ dirty ? '撤销该项' : '恢复默认' }}</NButton>
    </div>
  </div>
</template>

<style scoped>
.setting-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; padding: 20px 0; border-bottom: 1px solid #313244; }
.setting-row:last-child { border-bottom: 0; }
.setting-row.dirty { border-left: 3px solid #f9e2af; padding-left: 14px; }
.setting-info { min-width: 0; flex: 1; }
.setting-title { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; font-weight: 600; color: #cdd6f4; }
.category-label { color: #9399b2; font-size: 11px; font-weight: 400; }
.variable { display: block; color: #89b4fa; font-size: 11px; margin-top: 5px; overflow-wrap: anywhere; }
.description { color: #a6adc8; line-height: 1.65; font-size: 12px; margin-top: 6px; max-width: 680px; }
.metadata { display: flex; flex-wrap: wrap; gap: 5px 14px; margin-top: 7px; font-size: 11px; color: #7f849c; }
.metadata .risk { color: #f9e2af; }
.setting-control { width: 160px; flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; padding-top: 2px; }
.setting-control.wide { width: min(34%, 340px); min-width: 180px; }
.setting-control :deep(.n-input-number), .setting-control :deep(.n-select), .setting-control :deep(.n-input) { width: 100%; }
.inactive .description, .inactive .setting-title { opacity: .55; }
.disabled-reason { color: #9399b2; font-size: 11px; margin-top: 5px; }
.reset-button { color: #9399b2; }
@media (max-width: 900px) {
  .setting-row { flex-direction: column; gap: 12px; }
  .setting-control, .setting-control.wide { width: 100%; min-width: 0; align-items: flex-start; }
}
</style>
