<script setup lang="ts">
import type { SearchHit } from '../api'
import { pdfUrl } from '../api'

defineProps<{ hit: SearchHit }>()
</script>

<template>
  <details v-if="hit.retrieval_trace || hit.evidence_refs?.length || hit.structured_facts?.length" class="evidence" @click.stop>
    <summary>证据与检索线索（实验）</summary>
    <p v-if="hit.evidence_refs?.length" class="note">
      本页选取 {{ hit.evidence_refs.length }} 个原文窗口；各窗口按块引用核对，不代表全文。
    </p>
    <div v-if="hit.retrieval_trace" class="trace">
      <span>{{ hit.retrieval_trace.kind === 'entity_expansion' ? '共享实体扩展' : '实体直接命中' }}</span>
      <a v-if="hit.retrieval_trace.seed_file" :href="pdfUrl(hit.retrieval_trace.seed_file, hit.retrieval_trace.seed_page)" target="_blank" rel="noopener">
        种子第 {{ hit.retrieval_trace.seed_page }} 页
      </a>
      <span v-if="hit.retrieval_trace.shared_entities?.length">{{ hit.retrieval_trace.shared_entities.join(' · ') }}</span>
      <p class="note">检索连接不证明兼容、因果或工作条件相同。</p>
    </div>
    <div v-if="hit.structured_facts?.length" class="facts">
      <p class="note">明确表头的保守行列投影；数值、单位和条件均保留原文，空条件不是“无条件适用”。</p>
      <table>
        <thead><tr><th>参数</th><th>原值</th><th>单位</th><th>条件</th></tr></thead>
        <tbody>
          <tr v-for="fact in hit.structured_facts" :key="`${fact.source.chunk_id}:${fact.source.start_offset}`">
            <td>{{ fact.parameter }}<span v-if="fact.symbol"> ({{ fact.symbol }})</span></td>
            <td><div v-for="(value, role) in fact.values" :key="role">{{ role }}: {{ value }}</div></td>
            <td>{{ fact.unit }}</td>
            <td>{{ fact.conditions || '原行未注明' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </details>
</template>

<style scoped>
.evidence { margin-top: 10px; font-size: 12px; color: #a6adc8; border-top: 1px solid #313244; padding-top: 8px; }
.evidence summary { cursor: pointer; }
.trace { display: flex; flex-wrap: wrap; gap: 8px; padding-top: 8px; }
.note { color: #9399b2; margin: 6px 0; }
.trace .note { width: 100%; margin-top: 0; }
.trace a { color: #89b4fa; }
.facts { overflow-x: auto; }
.facts table { border-collapse: collapse; width: 100%; text-align: left; }
.facts th, .facts td { border: 1px solid #45475a; padding: 6px; vertical-align: top; white-space: pre-wrap; }
</style>
