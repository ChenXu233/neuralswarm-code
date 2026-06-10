<script setup lang="ts">
import { MessageSquare, Folder, Puzzle, Settings, Database } from 'lucide-vue-next'

const props = defineProps<{
  activePanel: 'chat' | 'files' | 'plugins' | 'memory' | null
  showSettings: boolean
}>()

const emit = defineEmits<{
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'memory' | null]
  'toggleSettings': []
}>()

function handleClick(panel: 'chat' | 'files' | 'plugins' | 'memory') {
  // Close settings if open when switching panels
  if (props.showSettings) {
    emit('toggleSettings')
  }
  emit('update:activePanel', props.activePanel === panel ? null : panel)
}

function handleSettingsClick() {
  emit('toggleSettings')
}
</script>

<template>
  <div class="activity-bar">
    <div class="activity-logo">N</div>

    <div class="top-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'chat' && !showSettings }]"
        :title="$t('activity.chat')"
        @click="handleClick('chat')"
      >
        <MessageSquare />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'files' && !showSettings }]"
        :title="$t('activity.files')"
        @click="handleClick('files')"
      >
        <Folder />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'plugins' && !showSettings }]"
        :title="$t('activity.plugins')"
        @click="handleClick('plugins')"
      >
        <Puzzle />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'memory' && !showSettings }]"
        :title="$t('activity.memory')"
        @click="handleClick('memory')"
      >
        <Database />
      </button>
    </div>

    <div class="bottom-icons">
      <button
        :class="['activity-btn', { active: showSettings }]"
        :title="$t('activity.settings')"
        @click="handleSettingsClick"
      >
        <Settings />
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
  padding: 0.5rem 0;
  gap: 4px;
}

.activity-logo {
  width: 2.125rem;
  height: 2.125rem;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg);
  font-size: 0.9375rem;
  font-weight: var(--font-semibold);
  margin-bottom: 0.5rem;
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
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  position: relative;
  font-size: 1.25rem;
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
  left: -0.5625rem;
  top: 0.375rem;
  bottom: 0.375rem;
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
