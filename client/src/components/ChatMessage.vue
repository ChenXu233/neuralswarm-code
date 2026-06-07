<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
}>()

const md = new MarkdownIt()
const html = computed(() => md.render(props.content))
</script>

<template>
  <div :class="['message', role]">
    <div v-if="role === 'assistant'" class="role-label">Agent</div>
    <div class="content" v-html="html"></div>
  </div>
</template>

<style scoped>
.message {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

.role-label {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-bottom: 4px;
  font-weight: 500;
}

.content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  font-size: 13px;
  line-height: 1.6;
}

.message.user .content {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
}

.message.assistant .content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
}

.content :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 8px 0;
}

.content :deep(code) {
  font-family: var(--font-mono);
  font-size: 12px;
}

.content :deep(p) {
  margin-bottom: 8px;
}

.content :deep(p:last-child) {
  margin-bottom: 0;
}
</style>
