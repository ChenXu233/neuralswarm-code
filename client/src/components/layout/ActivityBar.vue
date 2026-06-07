<script setup lang="ts">
import { MessageSquare, Folder, Puzzle, Settings } from 'lucide-vue-next'
import IconButton from '../ui/IconButton.vue'

defineProps<{
  activePanel: 'chat' | 'files' | 'plugins' | 'settings'
}>()

defineEmits<{
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings']
}>()
</script>

<template>
  <div class="activity-bar">
    <div class="top-icons">
      <IconButton
        :active="activePanel === 'chat'"
        tooltip="对话"
        @click="$emit('update:activePanel', 'chat')"
      >
        <MessageSquare :size="18" />
      </IconButton>
      <IconButton
        :active="activePanel === 'files'"
        tooltip="文件"
        @click="$emit('update:activePanel', 'files')"
      >
        <Folder :size="18" />
      </IconButton>
      <IconButton
        :active="activePanel === 'plugins'"
        tooltip="插件"
        @click="$emit('update:activePanel', 'plugins')"
      >
        <Puzzle :size="18" />
      </IconButton>
    </div>
    <div class="bottom-icons">
      <IconButton
        :active="activePanel === 'settings'"
        tooltip="设置"
        @click="$emit('update:activePanel', 'settings')"
      >
        <Settings :size="18" />
        <span class="connection-dot"></span>
      </IconButton>
    </div>
  </div>
</template>

<style scoped>
.activity-bar {
  width: var(--activity-bar-width);
  background-color: var(--color-activity-bg);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  gap: 4px;
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

.connection-dot {
  position: absolute;
  right: 3px;
  bottom: 3px;
  width: 7px;
  height: 7px;
  background-color: var(--color-success);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-activity-bg);
}
</style>
