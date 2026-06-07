<script setup lang="ts">
defineProps<{ tool: string; args: any; output?: string }>()

function formatArgs(args: any): string {
  return JSON.stringify(args, null, 2)
}
</script>

<template>
  <div class="tool-call">
    <div class="header">
      <span class="icon">&#x1f527;</span>
      <span class="name">{{ tool }}</span>
    </div>
    <pre class="code-block"><code>{{ formatArgs(args) }}</code></pre>
    <div v-if="output" class="output">
      <div class="label">Output:</div>
      <pre class="code-block"><code>{{ output }}</code></pre>
    </div>
  </div>
</template>

<style scoped>
.tool-call { margin: 8px 0; padding: 12px; background: var(--color-surface, #fafafa); border: 1px solid var(--color-border, #e8e8e8); border-radius: 8px; }
.header { font-weight: 500; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.icon { font-size: 14px; }
.name { font-size: 13px; font-weight: 600; color: var(--color-text, #333); }
.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  overflow-x: auto;
  line-height: 1.5;
  margin: 0;
}
.code-block code {
  white-space: pre;
}
.output { margin-top: 10px; }
.label { font-size: 11px; color: var(--color-text-tertiary, #999); margin-bottom: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.output .code-block {
  max-height: 300px;
  overflow-y: auto;
}
</style>
