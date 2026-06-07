<script setup lang="ts">
import { MessageSquare, Folder, Puzzle, Settings } from 'lucide-vue-next'

const props = defineProps<{
  activePanel: 'chat' | 'files' | 'plugins' | 'settings' | null
}>()

const emit = defineEmits<{
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings' | null]
}>()

function handleClick(panel: 'chat' | 'files' | 'plugins' | 'settings') {
  // Toggle: if same panel is clicked, collapse; otherwise switch
  emit('update:activePanel', props.activePanel === panel ? null : panel)
}
</script>

<template>
  <div class="activity-bar">
    <div class="activity-logo">N</div>

    <div class="top-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'chat' }]"
        title="Chat"
        @click="handleClick('chat')"
      >
        <MessageSquare :size="20" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'files' }]"
        title="Files"
        @click="handleClick('files')"
      >
        <Folder :size="20" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'plugins' }]"
        title="Plugins"
        @click="handleClick('plugins')"
      >
        <Puzzle :size="20" />
      </button>
    </div>

    <div class="bottom-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'settings' }]"
        title="Settings"
        @click="handleClick('settings')"
      >
        <Settings :size="20" />
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
  gap: 4px;
}

.activity-logo {
  width: 34px;
  height: 34px;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg);
  font-size: 15px;
  font-weight: var(--font-semibold);
  margin-bottom: 8px;
}

.top-icons, .bottom-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.top-icons {
  flex: 1;
}

.bottom-icons {
  position: relative;
}

.activity-btn {
  width: 36px;
  height: 36px;
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
