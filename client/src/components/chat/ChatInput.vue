<script setup lang="ts">
import { ref } from 'vue'
import { Send, Paperclip } from 'lucide-vue-next'

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
        placeholder="继续任务..."
        @keydown="handleKeydown"
      ></textarea>
      <div class="input-actions">
        <button class="action-btn" title="附件">
          <Paperclip :size="14" />
        </button>
        <button
          class="send-btn"
          :disabled="loading || !text.trim()"
          @click="handleSubmit"
        >
          <Send :size="14" />
          <span>{{ loading ? '发送中...' : '发送' }}</span>
        </button>
      </div>
    </div>
    <div class="input-hint">
      ⌘↵ 发送 · / 命令
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.input-wrapper {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 12px;
}

.input-wrapper textarea {
  width: 100%;
  min-height: 40px;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: 13px;
  color: var(--color-text);
  resize: none;
  outline: none;
}

.input-wrapper textarea::placeholder {
  color: var(--color-text-tertiary);
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  padding: 6px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
}

.action-btn:hover {
  background: var(--color-surface-hover);
}

.send-btn {
  padding: 6px 14px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  text-align: center;
  margin-top: 6px;
  font-size: 10px;
  color: var(--color-text-tertiary);
}
</style>
