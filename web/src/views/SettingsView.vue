<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { NAlert, NButton, NCollapse, NCollapseItem, NEmpty, NInput, NPopconfirm, NSpin, NSwitch, NTag, useMessage } from 'naive-ui'
import SettingField from '../components/settings/SettingField.vue'
import { commonNames, matchesSetting, sectionOf, sections } from '../components/settings/catalog'
import { useSettings } from '../composables/useSettings'

const { payload, specs, draft, loading, saving, error, dirtyNames, update, revert, load, save, reset } = useSettings()
const message = useMessage()
const page = ref<HTMLElement | null>(null)
const active = shallowRef('common')
const query = shallowRef('')
const changedOnly = shallowRef(false)
const expanded = ref<string[]>([])
const showVariables = shallowRef(localStorage.getItem('settings_show_var') === '1')
const searching = computed(() => query.value.trim().length > 0)
const current = computed(() => sections.find((section) => section.id === active.value))
const allNames = computed(() => {
  const ordered = sections.flatMap((section) => [...section.primary, ...section.advanced])
  return [...ordered.filter((name) => specs.value[name]), ...Object.keys(specs.value).filter((name) => !ordered.includes(name))]
})
const filteredNames = computed(() => allNames.value.filter((name) =>
  (!changedOnly.value || dirtyNames.value.includes(name)) && matchesSetting(name, specs.value[name]!, query.value)))
const directList = computed(() => searching.value || changedOnly.value || active.value === 'common' || active.value === 'other')
const primaryNames = computed(() => {
  if (searching.value || changedOnly.value) return filteredNames.value
  if (active.value === 'common') return commonNames.filter((name) => specs.value[name])
  if (active.value === 'other') return allNames.value.filter((name) => !sectionOf(name))
  return current.value?.primary.filter((name) => specs.value[name]) ?? []
})
const advancedNames = computed(() => current.value?.advanced.filter((name) => specs.value[name]) ?? [])
const unknownNames = computed(() => allNames.value.filter((name) => !sectionOf(name)))
const navigation = computed(() => [
  { id: 'common', title: '常用设置', description: '并发、模型和返回结果', names: commonNames.filter((name) => specs.value[name]) },
  ...sections.map((section) => ({ ...section, names: [...section.primary, ...section.advanced].filter((name) => specs.value[name]) })),
  ...(unknownNames.value.length ? [{ id: 'other', title: '其他设置', description: '尚未分类的参数', names: unknownNames.value }] : []),
])
const title = computed(() => searching.value ? `搜索结果（${primaryNames.value.length}）`
  : changedOnly.value ? '未保存的改动' : active.value === 'common' ? '常用设置' : active.value === 'other' ? '其他设置' : current.value?.title)
const subtitle = computed(() => searching.value ? '已跨所有分类搜索，包含高级设置。支持中文名称、说明和变量名。'
  : changedOnly.value ? '集中检查即将保存的值。切换分类不会丢失草稿。'
  : active.value === 'common' ? '先从最常调整的项目开始，其余参数按任务分类。' : current.value?.description)

function selectCategory(id: string) {
  active.value = id
  query.value = ''
  changedOnly.value = false
  expanded.value = []
  page.value?.scrollIntoView({ block: 'start' })
}
async function saveDraft() {
  const guarded = ['embed_model', 'embed_dimensions', 'embed_input_type_doc', 'embed_input_type_query']
  if (dirtyNames.value.some((name) => guarded.includes(name))
      && !window.confirm('将修改嵌入模型、维度或输入类型，必须与已有向量分区匹配；不会自动重建索引。确认保存吗？')) return
  await save()
}
function resetField(name: string) {
  if (dirtyNames.value.includes(name)) {
    draft.value[name] = specs.value[name]!.value
    message.info('已撤销该项未保存的改动。')
    return
  }
  return reset([name])
}
function toggleChanged() {
  changedOnly.value = !changedOnly.value
  if (changedOnly.value) query.value = ''
}
function modifiedCount(names: string[]) { return names.filter((name) => dirtyNames.value.includes(name)).length }
function disabledReason(name: string): string {
  const backend = String(draft.value.ocr_backend ?? '').toLowerCase()
  if (name === 'ocr_url' && backend !== 'local') return '当前选择远程后端，本机 OCR 地址不参与请求。'
  if (['ocr_api_base', 'ocr_model', 'ocr_prompt'].includes(name) && backend !== 'remote') return '当前选择本地后端，切换为远程后可编辑。'
  return ''
}
function toggleVariables(value: boolean) {
  showVariables.value = value
  localStorage.setItem('settings_show_var', value ? '1' : '0')
}
function beforeUnload(event: BeforeUnloadEvent) {
  if (!dirtyNames.value.length) return
  event.preventDefault()
  event.returnValue = ''
}
onMounted(() => window.addEventListener('beforeunload', beforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
onBeforeRouteLeave(() => !dirtyNames.value.length || window.confirm('有未保存的配置改动，确定离开并丢弃草稿吗？'))
</script>

<template>
  <div ref="page" class="settings-page">
    <header class="page-header">
      <div><h2>配置中心</h2><p>按任务查找设置，不必逐项翻阅参数。</p></div>
      <div class="header-tools"><span>显示变量名</span><NSwitch :value="showVariables" size="small" aria-label="显示变量名" @update:value="toggleVariables" /></div>
    </header>

    <div class="search-bar">
      <NInput v-model:value="query" clearable placeholder="搜索设置，例如：并发、OCR、模型、超时…" :input-props="{ 'aria-label': '搜索配置' }" />
      <NButton :type="changedOnly ? 'primary' : 'default'" :secondary="changedOnly" @click="toggleChanged">未保存 {{ dirtyNames.length }}</NButton>
    </div>
    <NAlert v-if="error" type="error" class="notice">读取配置失败：{{ error }} <NButton text @click="load">重试</NButton></NAlert>

    <NSpin :show="loading">
      <div v-if="payload" class="settings-layout">
        <nav class="category-nav" aria-label="配置分类">
          <button v-for="item in navigation" :key="item.id" type="button" class="category-button"
            :class="{ selected: active === item.id && !searching && !changedOnly }"
            :aria-current="active === item.id && !searching && !changedOnly ? 'page' : undefined"
            @click="selectCategory(item.id)">
            <span class="category-heading">{{ item.title }}<span v-if="modifiedCount(item.names)" class="modified-dot">{{ modifiedCount(item.names) }}</span></span>
            <span class="category-description">{{ item.description }}</span>
          </button>
          <div class="nav-note">检索参数保存后即时生效。<br>索引设置由下一轮任务使用。</div>
        </nav>

        <main class="settings-content">
          <div class="section-header"><div><h3>{{ title }}</h3><p>{{ subtitle }}</p></div><NTag :bordered="false">{{ primaryNames.length + (!directList ? advancedNames.length : 0) }} 项</NTag></div>
          <NAlert v-if="!directList && current?.hint" type="info" :show-icon="false" class="section-hint">{{ current.hint }}</NAlert>
          <NAlert v-if="active === 'common' && !searching && !changedOnly" type="info" :show-icon="false" class="section-hint">本地解析与 OCR 请求并发可独立设置。更换嵌入模型前，请确认已有向量分区与模型、维度匹配。</NAlert>
          <div class="field-list">
            <SettingField v-for="name in primaryNames" :key="name" :name="name" :spec="specs[name]!" :value="draft[name]!"
              :dirty="dirtyNames.includes(name)" :disabled="Boolean(disabledReason(name))" :disabled-reason="disabledReason(name)"
              :busy="saving" :show-variables="showVariables" :category="directList ? sectionOf(name)?.title : undefined"
              @change="update(name, $event)" @reset="resetField(name)" />
          </div>
          <NEmpty v-if="!primaryNames.length && directList" description="没有匹配的设置。试试“并发”“OCR”或参数变量名。" class="empty-state" />
          <NCollapse v-if="!directList && advancedNames.length" v-model:expanded-names="expanded" class="advanced">
            <NCollapseItem name="advanced" :title="`高级设置 · ${advancedNames.length} 项`">
              <p class="advanced-note">通常无需修改；展开后仍保留原有说明、取值范围和默认值。</p>
              <SettingField v-for="name in advancedNames" :key="name" :name="name" :spec="specs[name]!" :value="draft[name]!"
                :dirty="dirtyNames.includes(name)" :disabled="Boolean(disabledReason(name))" :disabled-reason="disabledReason(name)"
                :busy="saving" :show-variables="showVariables" @change="update(name, $event)" @reset="resetField(name)" />
            </NCollapseItem>
          </NCollapse>
        </main>
      </div>
    </NSpin>

    <footer v-if="payload" class="save-bar">
      <div><strong>{{ dirtyNames.length ? `${dirtyNames.length} 项未保存` : '所有改动已保存' }}</strong><span class="save-hint">切换分类保留草稿；保存作用于全部分类。</span></div>
      <div class="save-actions">
        <NPopconfirm :to="'.settings-page'" @positive-click="reset()"><template #trigger><NButton quaternary :disabled="saving">全部恢复默认</NButton></template>恢复全部设置为环境变量或内置默认值，并立即保存？</NPopconfirm>
        <NButton :disabled="!dirtyNames.length || saving" @click="revert">撤销改动</NButton>
        <NButton type="primary" :loading="saving" :disabled="!dirtyNames.length" @click="saveDraft">保存全部改动</NButton>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.settings-page { max-width: 1280px; margin: 0 auto; padding-bottom: 12px; }
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 22px; }
.page-header h2 { margin: 0; font-size: 23px; }
.page-header p, .section-header p { margin: 6px 0 0; color: #9399b2; font-size: 13px; line-height: 1.6; }
.header-tools { display: flex; align-items: center; gap: 10px; color: #9399b2; font-size: 12px; white-space: nowrap; }
.search-bar { display: flex; gap: 12px; margin-bottom: 22px; }
.search-bar :deep(.n-input) { flex: 1; }
.settings-layout { display: grid; grid-template-columns: 195px minmax(0, 1fr); gap: 24px; }
.category-nav { align-self: start; position: sticky; top: 0; display: flex; flex-direction: column; gap: 6px; }
.category-button { border: 1px solid #313244; border-radius: 0; color: #cdd6f4; background: transparent; text-align: left; padding: 12px; cursor: pointer; }
.category-button:hover { background: #1e1e2e; }
.category-button.selected { background: #1e1e2e; border-color: #45475a; border-left: 3px solid #89b4fa; }
.category-heading { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; }
.category-description { display: block; margin-top: 4px; color: #7f849c; font-size: 11px; line-height: 1.5; }
.selected .category-heading { color: #89b4fa; }
.modified-dot { min-width: 17px; text-align: center; font-size: 10px; color: #f9e2af; }
.nav-note { margin: 18px 12px; color: #6c7086; font-size: 11px; line-height: 1.8; }
.settings-content { min-width: 0; border: 1px solid #313244; border-radius: 0; background: #1e1e2e; padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 18px; }
.section-header h3 { font-size: 18px; margin: 0; }
.section-hint { margin-bottom: 6px; font-size: 12px; }
.advanced { margin-top: 24px; padding-top: 18px; border-top: 1px solid #45475a; }
.advanced-note { color: #7f849c; font-size: 12px; }
.empty-state { padding: 48px 0; }
.notice { margin-bottom: 18px; }
.save-bar { position: sticky; bottom: 0; z-index: 5; display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-top: 24px; padding: 15px 18px; border: 1px solid #45475a; border-radius: 0; background: #181825; }
/* 本页所有组件（含弹层）统一为直角，不引入另一套卡片与按钮语言。 */
.settings-page :deep(*) { border-radius: 0 !important; }
.save-bar strong { font-size: 13px; color: #cdd6f4; }
.save-hint { display: block; font-size: 11px; color: #7f849c; margin-top: 4px; }
.save-actions { display: flex; gap: 10px; align-items: center; }
@media (max-width: 1050px) {
  .settings-layout { grid-template-columns: 1fr; gap: 14px; }
  .category-nav { position: static; display: flex; flex-direction: row; flex-wrap: wrap; gap: 6px; }
  .category-button { padding: 8px 12px; }
  .category-description, .nav-note { display: none; }
  .category-heading { font-size: 12px; gap: 8px; }
  .settings-content { padding: 18px; }
  .save-bar { flex-wrap: wrap; }
  .save-actions { margin-left: auto; flex-wrap: wrap; }
}
@media (max-width: 600px) {
  .page-header { align-items: flex-start; flex-direction: column; }
  .save-actions { margin-left: 0; }
}
</style>
