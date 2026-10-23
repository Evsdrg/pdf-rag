import { computed, onMounted, ref, shallowRef } from 'vue'
import { useMessage } from 'naive-ui'
import { getConfig, resetConfig, saveConfig, type ConfigPayload } from '../api'

export type SettingValue = number | boolean | string

export function useSettings() {
  const message = useMessage()
  const payload = ref<ConfigPayload | null>(null)
  const draft = ref<Record<string, SettingValue>>({})
  const loading = shallowRef(false)
  const saving = shallowRef(false)
  const error = shallowRef('')
  const specs = computed(() => payload.value?.specs ?? {})
  const dirtyNames = computed(() => Object.keys(draft.value).filter((name) =>
    specs.value[name] && draft.value[name] !== specs.value[name].value))

  function update(name: string, value: SettingValue) {
    if (!saving.value && specs.value[name]) draft.value[name] = value
  }

  function revert() {
    draft.value = Object.fromEntries(Object.entries(specs.value).map(([name, spec]) => [name, spec.value]))
  }

  async function load() {
    loading.value = true
    error.value = ''
    try {
      payload.value = await getConfig()
      revert()
    } catch (cause) {
      error.value = (cause as Error).message
    } finally {
      loading.value = false
    }
  }

  async function save() {
    if (saving.value) return
    const changed = Object.fromEntries(dirtyNames.value.map((name) => [name, draft.value[name]]))
    if (!Object.keys(changed).length) return
    saving.value = true
    try {
      const result = await saveConfig(changed)
      if (payload.value) payload.value.specs = result.specs
      for (const name of Object.keys(changed)) draft.value[name] = result.specs[name]!.value
      message.success(`已保存 ${Object.keys(changed).length} 项；索引设置在下一轮任务生效`)
    } catch (cause) {
      message.error(`保存失败：${(cause as Error).message}`)
    } finally {
      saving.value = false
    }
  }

  async function reset(names?: string[]) {
    if (saving.value) return
    saving.value = true
    try {
      const result = await resetConfig(names)
      if (payload.value) payload.value.specs = result.specs
      if (names) {
        for (const name of names) draft.value[name] = result.specs[name]!.value
      } else {
        revert()
      }
      message.success(names ? '该项已恢复默认' : '全部已恢复默认')
    } catch (cause) {
      message.error(`重置失败：${(cause as Error).message}`)
    } finally {
      saving.value = false
    }
  }

  onMounted(load)
  return { payload, specs, draft, loading, saving, error, dirtyNames, update, revert, load, save, reset }
}
