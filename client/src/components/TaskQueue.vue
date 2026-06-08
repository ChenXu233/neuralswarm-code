<script setup lang="ts">
import type { Task } from '../types/scheduler'

defineProps<{
  tasks: Task[]
}>()

const statusColors: Record<string, string> = {
  pending: '#faad14',
  running: '#1890ff',
  completed: '#52c41a',
  failed: '#ff4d4f',
  cancelled: '#999',
}
</script>

<template>
  <div class="task-queue">
    <h3>Task Queue</h3>
    <div v-if="tasks.length === 0" class="empty">No tasks in queue</div>
    <div v-for="task in tasks" :key="task.id" class="task-card">
      <div class="task-header">
        <span class="task-id">{{ task.id.slice(0, 8) }}</span>
        <span class="task-status" :style="{ color: statusColors[task.status] || '#666' }">{{ task.status }}</span>
      </div>
      <div class="task-prompt">{{ task.input }}</div>
    </div>
  </div>
</template>

<style scoped>
.task-queue {
  padding: 16px;
  background: var(--color-surface, #fff);
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border, #e5e5e5);
}

.task-queue h3 {
  margin: 0 0 12px;
  font-size: var(--text-base, 14px);
  font-weight: var(--font-semibold, 600);
  color: var(--color-text, #1a1a1a);
}

.empty {
  color: var(--color-text-tertiary, #999);
  font-size: var(--text-sm, 13px);
  padding: 8px 0;
}

.task-card {
  padding: 10px 12px;
  border: 1px solid var(--color-border, #e5e5e5);
  border-radius: var(--radius-sm, 4px);
  margin-bottom: 8px;
  transition: background-color var(--transition-fast, 150ms);
}

.task-card:hover {
  background: var(--color-surface-hover, #f5f5f5);
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.task-id {
  font-family: var(--font-mono, monospace);
  font-size: var(--text-xs, 11px);
  color: var(--color-text-tertiary, #999);
}

.task-status {
  font-size: var(--text-xs, 11px);
  font-weight: var(--font-medium, 500);
  text-transform: capitalize;
}

.task-prompt {
  font-size: var(--text-sm, 13px);
  color: var(--color-text, #1a1a1a);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
