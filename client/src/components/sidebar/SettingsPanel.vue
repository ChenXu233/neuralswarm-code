<script setup lang="ts">
import StatusDot from '../ui/StatusDot.vue'
import { useTheme } from '../../composables/useTheme'
import type { Theme } from '../../composables/useTheme'

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

const { theme, setTheme } = useTheme()

const themes: { value: Theme; label: string }[] = [
  { value: 'warm-stone', label: 'Warm Stone' },
  { value: 'dark-slate', label: 'Dark Slate' },
  { value: 'pure-minimal', label: 'Pure Minimal' },
  { value: 'amber-glow', label: 'Amber Glow' },
]
</script>

<template>
  <div class="settings-panel">
    <div class="panel-header">
      <span class="panel-title">SETTINGS</span>
    </div>

    <div class="settings-content">
      <!-- Servers -->
      <div class="section">
        <div class="section-label">SERVERS</div>
        <div
          v-for="server in servers"
          :key="server.url"
          :class="['setting-item', { active: server.url === activeServer }]"
          @click="$emit('select', server)"
        >
          <StatusDot :status="server.status" />
          <span class="item-label">{{ server.url }}</span>
          <span class="item-hint">{{ server.status === 'connected' ? 'connected' : 'offline' }}</span>
        </div>
        <button class="add-link">+ Add Server</button>
      </div>

      <!-- Theme -->
      <div class="section">
        <div class="section-label">THEME</div>
        <div
          v-for="t in themes"
          :key="t.value"
          :class="['setting-item', { active: theme === t.value }]"
          @click="setTheme(t.value)"
        >
          <span class="item-label">{{ t.label }}</span>
        </div>
      </div>

      <!-- Font -->
      <div class="section">
        <div class="section-label">FONT</div>
        <div class="font-input">
          <input placeholder="Custom font stack..." spellcheck="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  border-right: 1px solid var(--color-border);
  background: var(--color-surface);
  height: 100%;
}

.panel-header {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.section {
  margin-bottom: 16px;
}

.section-label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  font-weight: var(--font-semibold);
  letter-spacing: 1px;
  margin-bottom: 4px;
  padding: 0 8px;
}

.setting-item {
  padding: 6px 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.setting-item:hover {
  background: var(--color-surface-hover);
}

.setting-item.active {
  background: var(--color-activity-active);
  color: var(--color-accent);
}

.item-label {
  flex: 1;
  font-size: var(--text-sm);
}

.item-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.add-link {
  padding: 5px 8px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  width: 100%;
  margin-top: 2px;
  transition: border-color var(--transition-fast), color var(--transition-fast);
}

.add-link:hover {
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

.font-input {
  padding: 0 8px;
}

.font-input input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  font-size: var(--text-xs);
  color: var(--color-text);
  outline: none;
  font-family: var(--font-mono);
}

.font-input input:focus {
  border-color: var(--color-accent);
}
</style>
