<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  darkTheme,
  NConfigProvider,
  NGlobalStyle,
  NLayout,
  NLayoutSider,
  NLayoutContent,
  NMenu,
  NMessageProvider,
} from 'naive-ui'
import type { MenuOption } from 'naive-ui'

const router = useRouter()
const route = useRoute()

const menuOptions: MenuOption[] = [
  { label: '索引状态', key: 'status' },
  { label: '资料库', key: 'library' },
  { label: '文件库', key: 'files' },
  { label: '检索测试', key: 'search' },
  { label: '检索配置', key: 'settings' },
  { label: '数据管理', key: 'data' },
]

const activeKey = computed(() => route.name as string)

function onSelect(key: string) {
  router.push({ name: key })
}
</script>

<template>
  <n-config-provider :theme="darkTheme">
    <n-global-style />
    <n-message-provider>
      <n-layout has-sider style="height: 100vh">
        <n-layout-sider bordered width="200" :native-scrollbar="false" content-style="padding: 16px 12px">
          <div class="brand">PDF-RAG</div>
          <div class="subtitle">元器件手册检索</div>
          <n-menu :options="menuOptions" :value="activeKey" @update:value="onSelect" />
        </n-layout-sider>
        <n-layout-content content-style="padding: 24px; height: 100vh; overflow: auto">
          <router-view />
        </n-layout-content>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.brand {
  font-size: 18px;
  font-weight: 700;
  color: #89b4fa;
  letter-spacing: 1px;
}
.subtitle {
  font-size: 12px;
  color: #6c7086;
  margin: 4px 0 16px;
}
</style>

