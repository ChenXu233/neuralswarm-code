<script setup lang="ts">
interface Agent {
  id: string
  name: string
  agent_type: 'scheduler' | 'worker'
  status: 'idle' | 'planning' | 'running' | 'waiting' | 'completed' | 'failed'
  task_id: string | null
  parent_id: string | null
  created_at: string
}

defineProps<{
  agents: Agent[]
}>()

const statusColors: Record<string, string> = {
  idle: '#999',
  planning: '#1890ff',
  running: '#52c41a',
  waiting: '#faad14',
  completed: '#52c41a',
  failed: '#ff4d4f',
}
</script>

<template>
  <div class="agent-panel">
    <h3>Agents</h3>
    <div v-if="agents.length === 0" class="empty">No active agents</div>
    <div v-for="agent in agents" :key="agent.id" class="agent-card">
      <div class="agent-header">
        <span class="agent-name">{{ agent.name }}</span>
        <span class="agent-type" :class="agent.agent_type">{{ agent.agent_type }}</span>
      </div>
      <div class="agent-status">
        <span class="status-dot" :style="{ background: statusColors[agent.status] }"></span>
        {{ agent.status }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-panel {
  padding: 16px;
  background: var(--color-surface, #fff);
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border, #e5e5e5);
}

.agent-panel h3 {
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

.agent-card {
  padding: 10px 12px;
  border: 1px solid var(--color-border, #e5e5e5);
  border-radius: var(--radius-sm, 4px);
  margin-bottom: 8px;
  transition: background-color var(--transition-fast, 150ms);
}

.agent-card:hover {
  background: var(--color-surface-hover, #f5f5f5);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.agent-name {
  font-weight: var(--font-medium, 500);
  font-size: var(--text-sm, 13px);
  color: var(--color-text, #1a1a1a);
}

.agent-type {
  font-size: var(--text-xs, 11px);
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: var(--font-medium, 500);
}

.agent-type.scheduler {
  background: #e6f7ff;
  color: #1890ff;
}

.agent-type.worker {
  background: #f6ffed;
  color: #52c41a;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs, 11px);
  color: var(--color-text-secondary, #666);
  text-transform: capitalize;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
