<script setup lang="ts">
import { MessageSquare, Folder, Puzzle, Settings } from 'lucide-vue-next'

defineProps<{
  activePanel: 'chat' | 'files' | 'plugins' | 'settings'
}>()

defineEmits<{
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings']
}>()
</script>

<template>
  <div class="activity-bar">
    <!-- Logo -->
    <div class="activity-logo">N</div>

    <div class="top-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'chat' }]"
        title="Chat"
        @click="$emit('update:activePanel', 'chat')"
      >
        <MessageSquare :size="16" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'files' }]"
        title="Files"
        @click="$emit('update:activePanel', 'files')"
      >
        <Folder :size="16" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'plugins' }]"
        title="Plugins"
        @click="$emit('update:activePanel', 'plugins')"
      >
        <Puzzle :size="16" />
      </button>
    </div>

    <div class="bottom-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'settings' }]"
        title="Settings"
        @click="$emit('update:activePanel', 'settings')"
      >
        <Settings :size="16" />
        <span class="connection-dot"></span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.activity-bar {
  width: var(--activity-bar-width);
  background: var(--color-activity-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  gap: 6px;
}

/* Logo */
.activity-logo {
  width: 32px;
  height: 32px;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg);
  font-size: 14px;
  font-weight: var(--font-semibold);
  margin-bottom: 10px;
}

.top-icons, .bottom-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.top-icons {
  flex: 1;
}

.bottom-icons {
  position: relative;
}

/* Activity Button */
.activity-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  position: relative;
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.activity-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-surface-hover);
}

/* Active: left indicator line */
.activity-btn.active {
  color: var(--color-accent);
  background: var(--color-activity-active);
}

.activity-btn.active::before {
  content: '';
  position: absolute;
  left: -9px;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: var(--color-accent);
  border-radius: 0 2px 2px 0;
}

/* Connection dot */
.connection-dot {
  position: absolute;
  right: 2px;
  bottom: 2px;
  width: 7px;
  height: 7px;
  background-color: var(--color-success);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-activity-bg);
}
</style>
