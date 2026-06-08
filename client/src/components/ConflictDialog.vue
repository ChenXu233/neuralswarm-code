<script setup lang="ts">
interface Conflict {
  id: string
  file_path: string
  agent_id: string
  other_agent_id: string
  current_content: string
  new_content: string
  status: 'pending' | 'resolved' | 'timeout'
}

defineProps<{
  conflict: Conflict
}>()

const emit = defineEmits<{
  decide: [action: 're_read' | 'overwrite' | 'submit_to_scheduler']
}>()
</script>

<template>
  <div class="conflict-dialog">
    <h3>File Conflict: {{ conflict.file_path }}</h3>
    <div class="conflict-info">
      <p>Agent {{ conflict.agent_id }} wants to modify a file that was changed by Agent {{ conflict.other_agent_id }}</p>
    </div>
    <div class="diff-view">
      <div class="diff-side">
        <h4>Current Content</h4>
        <pre>{{ conflict.current_content }}</pre>
      </div>
      <div class="diff-side">
        <h4>New Content</h4>
        <pre>{{ conflict.new_content }}</pre>
      </div>
    </div>
    <div class="actions">
      <button @click="emit('decide', 're_read')">Re-read & Retry</button>
      <button @click="emit('decide', 'overwrite')" class="danger">Overwrite</button>
      <button @click="emit('decide', 'submit_to_scheduler')">Submit to Scheduler</button>
    </div>
  </div>
</template>

<style scoped>
.conflict-dialog {
  padding: 20px;
  background: var(--color-surface, #fff);
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border, #e5e5e5);
  max-width: 800px;
}

.conflict-dialog h3 {
  margin: 0 0 12px;
  font-size: var(--text-base, 14px);
  font-weight: var(--font-semibold, 600);
  color: var(--color-text, #1a1a1a);
}

.conflict-info {
  margin-bottom: 16px;
  padding: 10px 12px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: var(--radius-sm, 4px);
  font-size: var(--text-sm, 13px);
  color: #8c6e00;
}

.conflict-info p {
  margin: 0;
}

.diff-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.diff-side h4 {
  margin: 0 0 8px;
  font-size: var(--text-sm, 13px);
  font-weight: var(--font-medium, 500);
  color: var(--color-text-secondary, #666);
}

.diff-side pre {
  margin: 0;
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: var(--radius-sm, 4px);
  font-family: var(--font-mono, monospace);
  font-size: var(--text-xs, 12px);
  line-height: 1.6;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.actions button {
  padding: 8px 16px;
  border: 1px solid var(--color-border, #d9d9d9);
  border-radius: var(--radius-sm, 4px);
  background: var(--color-surface, #fff);
  color: var(--color-text, #1a1a1a);
  font-size: var(--text-sm, 13px);
  cursor: pointer;
  transition: all var(--transition-fast, 150ms);
}

.actions button:hover {
  border-color: var(--color-primary, #1890ff);
  color: var(--color-primary, #1890ff);
}

.actions button.danger {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.actions button.danger:hover {
  background: #ff4d4f;
  color: #fff;
}
</style>
