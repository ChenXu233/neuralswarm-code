<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'

defineProps<{
  tool: string
  args: any
  output?: string
}>()

const expanded = ref(false)

function toggle() {
  expanded.value = !expanded.value
}

function formatJson(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}
</script>

<template>
  <div :class="['tool-call', { expanded }]">
    <!-- Collapsed header -->
    <div class="tool-header" @click="toggle">
      <ChevronRight v-if="!expanded" :size="12" class="chevron" />
      <ChevronDown v-else :size="12" class="chevron" />
      <span class="tool-bullet">◆</span>
      <span class="tool-name">{{ tool }}</span>
      <span v-if="output" class="tool-stat done">done</span>
      <span v-else class="tool-stat pending">...</span>
    </div>

    <!-- Expanded body -->
    <Transition name="expand">
      <div v-if="expanded" class="tool-body">
        <!-- Parameters -->
        <div class="tool-section">
          <div class="tool-section-label">PARAMETERS</div>
          <pre class="tool-code">{{ formatJson(args) }}</pre>
        </div>

        <!-- Result -->
        <div v-if="output" class="tool-section result-section">
          <div class="tool-section-label">RESULT</div>
          <pre class="tool-code">{{ output }}</pre>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tool-call {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  transition: border-color var(--transition-fast);
  animation: message-in var(--transition-normal) var(--ease-out);
}

.tool-call.expanded {
  border-left-color: var(--color-accent);
}

/* Header */
.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.tool-header:hover {
  background: var(--color-surface-hover);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.tool-bullet {
  color: var(--color-accent);
  font-size: 8px;
  flex-shrink: 0;
}

.tool-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-accent);
  flex: 1;
}

.tool-stat {
  font-size: var(--text-xs);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.tool-stat.done {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.tool-stat.pending {
  color: var(--color-text-tertiary);
}

/* Body */
.tool-body {
  overflow: hidden;
}

.tool-section {
  padding: 8px 14px;
  border-top: 1px solid var(--color-border);
}

.tool-section.result-section {
  background: var(--color-surface-hover);
}

.tool-section-label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.tool-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.6;
}
</style>
