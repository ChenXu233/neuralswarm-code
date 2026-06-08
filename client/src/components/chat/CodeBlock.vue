<script setup lang="ts">
import { ref } from 'vue'
import { Copy, Check } from 'lucide-vue-next'

defineProps<{
  code: string
  language?: string
}>()

const copied = ref(false)

async function handleCopy(code: string) {
  await navigator.clipboard.writeText(code)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}
</script>

<template>
  <div class="code-block">
    <div class="code-header">
      <span class="language">{{ language || 'plaintext' }}</span>
      <button class="copy-btn" @click="handleCopy(code)">
        <Check v-if="copied" />
        <Copy v-else />
        <span>{{ copied ? 'Copied' : 'Copy' }}</span>
      </button>
    </div>
    <pre><code>{{ code }}</code></pre>
  </div>
</template>

<style scoped>
.code-block {
  background: #1e1e1e;
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 8px 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.code-header {
  padding: 5px 14px;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.language {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
  letter-spacing: 0.5px;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}

.copy-btn:hover {
  color: #ccc;
}

pre {
  padding: 12px 16px;
  margin: 0;
  overflow-x: auto;
}

code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.7;
  color: #d4d4d4;
}
</style>
