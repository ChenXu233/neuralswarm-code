<script setup lang="ts">
import StatusDot from '../ui/StatusDot.vue'

interface Server {
  url: string
  status: 'connected' | 'disconnected'
}

defineProps<{
  servers: Server[]
  activeServer?: string
}>()

defineEmits<{
  select: [server: Server]
}>()
</script>

<template>
  <div class="settings-panel">
    <div class="panel-header">
      <span class="panel-title">设置</span>
    </div>
    <div class="settings-content">
      <div class="section">
        <div class="section-label">服务器</div>
        <div
          v-for="server in servers"
          :key="server.url"
          :class="['server-item', { active: server.url === activeServer }]"
          @click="$emit('select', server)"
        >
          <StatusDot :status="server.status" />
          <span class="server-url">{{ server.url }}</span>
          <span class="server-status">
            {{ server.status === 'connected' ? '已连接' : '未连接' }}
          </span>
        </div>
        <button class="add-server">
          + 添加服务器
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.section {
  padding: 8px;
}

.section-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.server-item {
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.server-item:hover {
  background: var(--color-surface-hover);
}

.server-item.active {
  background: #e6f7ff;
  border-left: 2px solid var(--color-accent);
}

.server-url {
  font-size: 11px;
  color: var(--color-text);
  flex: 1;
}

.server-status {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.add-server {
  padding: 6px 10px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: 10px;
  color: var(--color-text-tertiary);
  width: 100%;
  margin-top: 4px;
}

.add-server:hover {
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}
</style>
