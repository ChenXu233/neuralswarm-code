<script setup lang="ts">
import { Plus, Search } from 'lucide-vue-next'
import StatusDot from '../ui/StatusDot.vue'
import type { Task } from '../../api/client'

defineProps<{
  tasks: Task[]
  activeTaskId?: string
}>()

defineEmits<{
  select: [task: Task]
  create: []
}>()

function getStatusVariant(status: string) {
  switch (status) {
    case 'running': return 'running'
    case 'completed': return 'completed'
    case 'failed': return 'failed'
    default: return 'pending'
  }
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}
</script>

<template>
  <div class="chat-panel">
    <div class="search-box">
      <Search :size="12" />
      <input placeholder="搜索..." />
    </div>

    <div class="task-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        :class="['task-item', { active: task.id === activeTaskId }]"
        @click="$emit('select', task)"
      >
        <div class="task-title">{{ task.input.slice(0, 30) }}</div>
        <div class="task-meta">
          <StatusDot :status="getStatusVariant(task.status)" />
          <span class="task-status">{{ task.status }}</span>
          <span class="task-time">{{ formatTime(task.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.add-button {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.add-button:hover {
  background: var(--color-border);
}

.search-box {
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-surface-hover);
  margin: 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.search-box input {
  border: none;
  background: transparent;
  font-size: 11px;
  color: var(--color-text);
  outline: none;
  width: 100%;
}

.search-box input::placeholder {
  color: var(--color-text-tertiary);
}

.task-list {
  flex: 1;
  overflow-y: auto;
}

.task-item {
  padding: 10px 12px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  margin: 0 4px 2px;
}

.task-item:hover {
  background: var(--color-surface-hover);
}

.task-item.active {
  background: color-mix(in srgb, var(--color-accent) 10%, transparent);
  border-left: 3px solid var(--color-accent);
}

.task-title {
  font-size: 12px;
  color: var(--color-text);
  margin-bottom: 4px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-status {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.task-time {
  font-size: 10px;
  color: var(--color-text-tertiary);
  margin-left: auto;
}
</style>
