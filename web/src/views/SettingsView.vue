<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NAlert, NButton, NCollapse, NCollapseItem, NInput, NInputNumber, NSpace,
  NSpin, NSwitch, NTag, NTooltip, useMessage,
} from 'naive-ui'
import {
  getConfig, resetConfig, saveConfig,
  type ConfigPayload, type ConfigSpec,
} from '../api'

const message = useMessage()
const loading = ref(true)
const saving = ref(false)
const payload = ref<ConfigPayload | null>(null)
/** 编辑中的值:与已生效值分离,便于"未保存"提示与撤销 */
const draft = ref<Record<string, number | boolean | string>>({})
const groups = computed(() => payload.value?.groups ?? [])

function specsOf(group: string): [string, ConfigSpec][] {
  const specs = payload.value?.specs ?? {}
  return Object.entries(specs).filter(([, s]) => s.group === group)
}

const dirtyNames = computed(() =>
  Object.keys(draft.value).filter((n) => draft.value[n] !== payload.value?.specs[n]?.value),
)

async function load() {
  loading.value = true
  try {
    payload.value = await getConfig()
    draft.value = Object.fromEntries(
      Object.entries(payload.value.specs).map(([n, s]) => [n, s.value]),
    )
  } catch (e) {
    message.error(`读取配置失败:${(e as Error).message}`)
  } finally {
    loading.value = false
  }
}

async function save() {
  const changed = Object.fromEntries(dirtyNames.value.map((n) => [n, draft.value[n]]))
  if (!Object.keys(changed).length) return
  saving.value = true
  try {
    const r = await saveConfig(changed)
    if (payload.value) payload.value.specs = r.specs
    message.success(`已保存 ${Object.keys(changed).length} 项,即时生效`)
  } catch (e) {
    message.error(`保存失败:${(e as Error).message}`)
  } finally {
    saving.value = false
  }
}

async function reset(names?: string[]) {
  try {
    const r = await resetConfig(names)
    if (payload.value) payload.value.specs = r.specs
    if (names) {
      names.forEach((n) => { draft.value[n] = r.specs[n].value })
    } else {
      draft.value = Object.fromEntries(
        Object.entries(r.specs).map(([n, s]) => [n, s.value]),
      )
    }
    message.success(names ? '该项已恢复默认' : '全部已恢复默认')
  } catch (e) {
    message.error(`重置失败:${(e as Error).message}`)
  }
}

function revert() {
  if (!payload.value) return
  draft.value = Object.fromEntries(
    Object.entries(payload.value.specs).map(([n, s]) => [n, s.value]),
  )
}

/** 范围提示文案,避免用户靠试错发现边界 */
function rangeHint(s: ConfigSpec): string {
  if (s.kind === 'bool') return ''
  const lo = s.lo ?? ''
  const hi = s.hi ?? ''
  return lo !== '' || hi !== '' ? `${lo} ~ ${hi}` : ''
}

function isDirty(name: string): boolean {
  return draft.value[name] !== payload.value?.specs[name]?.value
}

/** OCR 项按 backend 联动:local 只认 ocr_url;remote 只认 api_base/model/prompt。
 *  两组混着用会误导(改了不生效的那组还显示"已覆盖")。 */
function ocrDisabled(name: string): boolean {
  const be = String(draft.value['ocr_backend'] ?? '').toLowerCase()
  if (name === 'ocr_url') return be !== 'local'
  if (name === 'ocr_api_base' || name === 'ocr_model' || name === 'ocr_prompt') return be !== 'remote'
  return false
}

/** 是否显示原始变量名(name)与 env 键。默认关(只显中文名),记住用户选择 */
const showVarNames = ref(localStorage.getItem('settings_show_var') === '1')
function toggleVarNames(v: boolean) {
  showVarNames.value = v
  localStorage.setItem('settings_show_var', v ? '1' : '0')
}

onMounted(load)
</script>

<template>
  <div class="page">
    <n-space align="center" justify="space-between" style="margin-bottom: 16px">
      <div>
        <h2 class="title">检索配置</h2>
        <div class="hint">
          改动即时生效并持久化到 <code>data/settings.json</code>;密钥、目录等部署项不在此列。
        </div>
      </div>
      <n-space align="center">
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-space align="center" :size="6" style="margin-right: 8px">
              <n-switch :value="showVarNames" size="small" @update:value="toggleVarNames" />
              <span class="var-lbl">变量名</span>
            </n-space>
          </template>
          显示原始变量名与 env 键(便于对照配置文件 / 与文档沟通)
        </n-tooltip>
        <n-tag v-if="dirtyNames.length" type="warning" round>
          {{ dirtyNames.length }} 项未保存
        </n-tag>
        <n-button :disabled="!dirtyNames.length" @click="revert">撤销改动</n-button>
        <n-button :disabled="!dirtyNames.length" @click="reset()">全部恢复默认</n-button>
        <n-button type="primary" :loading="saving" :disabled="!dirtyNames.length" @click="save">
          保存
        </n-button>
      </n-space>
    </n-space>

    <n-alert v-if="dirtyNames.length" type="warning" style="margin-bottom: 16px">
      有未保存的改动。检索参数(权重/候选深度/片段宽度)会直接影响结果质量,
      调整后建议到「检索测试」页复核。
    </n-alert>

    <n-spin :show="loading">
      <!-- 数据就绪后才渲染:default-expanded-names 是非受控绑定,只在首次挂载生效,
           若在 loading 期(groups 还是空)挂载,所有分组会永远折叠 -->
      <n-collapse v-if="payload" :default-expanded-names="groups">
        <n-collapse-item v-for="g in groups" :key="g" :name="g">
          <template #header>
            <span class="group">{{ g }}</span>
            <n-tag size="small" style="margin-left: 8px">{{ specsOf(g).length }} 项</n-tag>
          </template>

          <div class="grid">
            <div
              v-for="[name, spec] in specsOf(g)" :key="name"
              class="item" :class="{ dim: ocrDisabled(name) }"
            >
              <div class="head">
                <div class="name">
                  {{ spec.label }}
                  <code v-if="showVarNames" class="var">{{ name }}</code>
                  <n-tag v-if="spec.overridden" size="tiny" type="success" round>已覆盖</n-tag>
                  <n-tag v-if="isDirty(name)" size="tiny" type="warning" round>未保存</n-tag>
                </div>
                <div class="ctrl">
                  <n-switch
                    v-if="spec.kind === 'bool'"
                    :value="Boolean(draft[name])"
                    :disabled="ocrDisabled(name)"
                    @update:value="(v: boolean) => (draft[name] = v)"
                  />
                  <n-input-number
                    v-else-if="spec.kind === 'int' || spec.kind === 'float'"
                    :value="Number(draft[name])"
                    :min="spec.lo ?? undefined"
                    :max="spec.hi ?? undefined"
                    :step="spec.kind === 'int' ? 1 : 0.1"
                    :precision="spec.kind === 'float' ? 2 : 0"
                    :disabled="ocrDisabled(name)"
                    style="width: 150px"
                    @update:value="(v: number | null) => v !== null && (draft[name] = v)"
                  />
                  <n-input
                    v-else
                    :value="String(draft[name] ?? '')"
                    :disabled="ocrDisabled(name)"
                    style="width: 100%"
                    @update:value="(v: string) => (draft[name] = v)"
                  />
                  <n-tooltip v-if="spec.overridden" trigger="hover">
                    <template #trigger>
                      <n-button size="tiny" quaternary @click="reset([name])">恢复默认</n-button>
                    </template>
                    清除覆盖值,回到 env / 内置默认
                  </n-tooltip>
                </div>
              </div>
              <div class="desc">{{ spec.desc }}</div>
              <div class="src">
                默认 <b>{{ spec.default }}</b>
                <template v-if="showVarNames && spec.env_key"> · env <code>{{ spec.env_key }}</code></template>
                <template v-if="rangeHint(spec)"> · 范围 {{ rangeHint(spec) }}</template>
              </div>
            </div>
          </div>
        </n-collapse-item>
      </n-collapse>
    </n-spin>
  </div>
</template>

<style scoped>
/* 完全流式:不设页宽上限,列数由实际视口决定。
   auto-fit(而非 auto-fill):末行不满时空轨道塌掉、现有卡片拉伸填满,不留死白。
   340px 是卡片最小可读宽度,视口每多出一个 340+gap 就多一列。 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 10px 14px;
}
.title { margin: 0 0 4px; font-size: 20px; }
.hint { font-size: 12px; color: #6c7086; }
.hint code { color: #89b4fa; }
.group { font-weight: 600; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 10px 14px;
}
.item {
  border: 1px solid #313244;
  border-radius: 8px;
  background: #1e1e2e;
  padding: 10px 12px;
  min-width: 0;
}
/* 与当前 ocr_backend 无关的项:淡化提示,控件本身已禁用 */
.item.dim { opacity: 0.38; }
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap; /* str 长输入放不下时整体换到下一行 */
}
.name { font-size: 13px; font-weight: 600; color: #cdd6f4; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
/* 开关打开后跟在中文名后的原始变量名 */
.name .var { font-size: 11px; font-weight: 400; color: #89b4fa; background: #181825; padding: 1px 5px; border-radius: 4px; }
.var-lbl { font-size: 12px; color: #a6adc8; }
.desc { font-size: 12px; color: #a6adc8; margin-top: 4px; line-height: 1.5; }
.src { font-size: 11px; color: #6c7086; margin-top: 4px; }
.src code { color: #89b4fa; }
.ctrl { display: flex; align-items: center; gap: 8px; flex-shrink: 0; max-width: 100%; }
.ctrl:has(.n-input) { width: 100%; flex-shrink: 1; } /* 文本框独占一行时拉满 */
</style>
