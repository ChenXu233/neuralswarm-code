<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown, Pencil } from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  thinkingDone?: boolean
  streaming?: boolean
}>()

const emit = defineEmits<{
  edit: []
}>()

const md = new MarkdownIt()
const html = computed(() => md.render(props.content))
const thinkingExpanded = ref(false)
const showEdit = ref(false)

function toggleThinking() {
  thinkingExpanded.value = !thinkingExpanded.value
}
</script>

<template>
  <div :class="['message', role]">
    <!-- Thinking section -->
    <div v-if="thinking || (streaming && role === 'assistant')" class="thinking-section">
      <div
        :class="['thinking-toggle', { expanded: thinkingExpanded }]"
        @click="toggleThinking"
      >
        <ChevronRight v-if="!thinkingExpanded" class="chevron" />
        <ChevronDown v-else class="chevron" />
        <span class="thinking-label">{{ $t('thinking.label') }}</span>
        <span v-if="thinkingDone" class="thinking-duration">· {{ $t('common.done') }}</span>
        <span v-else class="thinking-duration">· ...</span>
      </div>
      <Transition name="expand">
        <div v-if="thinkingExpanded || (streaming && !thinkingDone)" class="thinking-content">
          {{ thinking || '' }}
          <span v-if="streaming && !thinkingDone" class="cursor-blink"></span>
        </div>
      </Transition>
    </div>

    <!-- User message: right aligned, filled -->
    <div
      v-if="role === 'user'"
      class="user-wrapper"
      @mouseenter="showEdit = true"
      @mouseleave="showEdit = false"
    >
      <button v-if="showEdit" class="edit-btn" @click="emit('edit')" title="Edit message">
        <Pencil />
      </button>
      <div class="user-content">
        {{ content }}
      </div>
    </div>

    <!-- Assistant message: left aligned, no bubble -->
    <div v-else class="assistant-content" v-html="html">
    </div>

    <!-- Streaming cursor (assistant content) -->
    <span v-if="streaming && role === 'assistant'" class="cursor-blink"></span>
  </div>
</template>

<style scoped>
.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  animation: message-in var(--transition-normal) var(--ease-out);
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

/* --- Thinking --- */
.thinking-section {
  margin-bottom: 8px;
  width: 100%;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  transition: background-color var(--transition-fast);
  user-select: none;
}

.thinking-toggle:hover {
  background: var(--color-surface-hover);
}

.thinking-label {
  font-weight: var(--font-medium);
}

.thinking-duration {
  color: var(--color-text-tertiary);
}

.chevron {
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.thinking-content {
  margin-top: 4px;
  padding: 6px 12px;
  border-left: 2px solid var(--color-border);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  line-height: 1.7;
  white-space: pre-wrap;
  overflow: hidden;
}

/* --- User --- */
.user-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  max-width: 75%;
}

.user-content {
  background: var(--color-primary);
  color: var(--color-bg);
  padding: 10px 14px;
  border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
  font-size: var(--text-base);
  line-height: 1.5;
  box-shadow: var(--shadow-sm);
}

.edit-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast), background-color var(--transition-fast);
}

.user-wrapper:hover .edit-btn {
  opacity: 1;
}

.edit-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

/* --- Assistant --- */
.assistant-content {
  max-width: 80%;
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--color-text);
}

/* Deep styles for markdown */
.assistant-content :deep(p) {
  margin-bottom: 8px;
}

.assistant-content :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-content :deep(ul), .assistant-content :deep(ol) {
  margin-bottom: 8px;
  padding-left: 20px;
}

.assistant-content :deep(li) {
  margin-bottom: 2px;
}

.assistant-content :deep(code) {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--color-surface-hover);
  padding: 1px 5px;
  border-radius: 3px;
}

.assistant-content :deep(pre) {
  background: #1e1e1e;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 8px 0;
}

.assistant-content :deep(pre code) {
  background: transparent;
  padding: 0;
  font-size: var(--text-sm);
  color: #d4d4d4;
}

.assistant-content :deep(strong) {
  font-weight: var(--font-semibold);
}

.assistant-content :deep(blockquote) {
  border-left: 2px solid var(--color-accent);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--color-text-secondary);
}
</style>
