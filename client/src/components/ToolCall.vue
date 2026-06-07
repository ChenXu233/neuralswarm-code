<script setup lang="ts">
import { Wrench, Check } from 'lucide-vue-next'

defineProps<{
  tool: string
  args: any
  output?: string
}>()
</script>

<template>
  <div class="tool-call">
    <div class="tool-header">
      <div class="tool-icon">
        <Wrench :size="14" />
      </div>
      <span class="tool-name">{{ tool }}</span>
      <span v-if="output" class="tool-status success">
        <Check :size="12" />
      </span>
    </div>
    <div v-if="output" class="tool-output">
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.tool-call {
  margin-bottom: 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  max-width: 65%;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-icon {
  width: 24px;
  height: 24px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.tool-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text);
}

.tool-status {
  display: flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: 10px;
}

.tool-status.success {
  background: #f6ffed;
  color: var(--color-success);
}

.tool-output {
  margin-top: 8px;
  padding: 8px 10px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-sm);
}

.tool-output pre {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-secondary);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
