<script setup lang="ts">
import { ref } from 'vue'
import { Send } from 'lucide-vue-next'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [text: string]
}>()

const text = ref('')

function handleSubmit() {
  if (!text.value.trim() || props.loading) return
  emit('submit', text.value)
  text.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <textarea
        v-model="text"
        placeholder="Type a message..."
        @keydown="handleKeydown"
        rows="1"
      ></textarea>
      <div class="input-actions">
        <span class="shortcut-hint">Ctrl ↵</span>
        <button
          class="send-btn"
          :disabled="loading || !text.trim()"
          @click="handleSubmit"
        >
          <Send :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  padding: 12px 16px 16px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 10px 16px;
  box-shadow: var(--shadow-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.input-wrapper:focus-within {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow);
}

.input-wrapper textarea {
  flex: 1;
  min-height: 24px;
  max-height: 120px;
  border: none;
  background: transparent;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  resize: none;
  outline: none;
  line-height: 1.5;
}

.input-wrapper textarea::placeholder {
  color: var(--color-text-tertiary);
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.shortcut-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-primary);
  color: var(--color-bg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast), opacity var(--transition-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
