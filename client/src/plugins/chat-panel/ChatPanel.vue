<script setup lang="ts">
import { Search, Plus } from 'lucide-vue-next'
import type { Session } from '@/api/client'

defineProps<{
  sessions: Session[]
  activeSessionId?: string
}>()

defineEmits<{
  select: [session: Session]
  'new-session': []
}>()

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}
</script>

<template>
  <div class="chat-panel">
    <!-- Header: title + add button -->
    <div class="panel-header">
      <span class="panel-title">{{ $t('chat.tasks') }}</span>
      <button class="add-btn" @click="$emit('new-session')">
        <Plus />
      </button>
    </div>

    <!-- Search -->
    <div class="search-box">
      <Search />
      <input :placeholder="$t('chat.filterTasks')" />
    </div>

    <!-- Session list -->
    <div class="task-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        :class="['task-item', { active: session.id === activeSessionId }]"
        @click="$emit('select', session)"
      >
        <div class="task-header">
          <span class="task-title">{{ session.id.slice(0, 8) }}...</span>
        </div>
        <div class="task-meta">
          <span class="task-status">{{ session.message_count }} 条消息</span>
          <span class="task-time">{{ formatTime(session.created_at) }}</span>
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.add-btn {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.add-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.search-box {
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-surface-hover);
  margin: 0 8px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  color: var(--color-text-tertiary);
  transition: border-color var(--transition-fast);
}

.search-box:focus-within {
  border-color: var(--color-border);
}

.search-box input {
  border: none;
  background: transparent;
  font-size: var(--text-xs);
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
  padding: 8px 12px;
  cursor: pointer;
  border-radius: var(--radius-md);
  margin: 0 4px 2px;
  transition: background-color var(--transition-fast);
}

.task-item:hover {
  background: var(--color-surface-hover);
}

.task-item.active {
  background: var(--color-activity-active);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}

.task-title {
  font-size: var(--text-sm);
  color: var(--color-text);
  font-weight: var(--font-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-left: 14px;
}

.task-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.task-time {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}
</style>