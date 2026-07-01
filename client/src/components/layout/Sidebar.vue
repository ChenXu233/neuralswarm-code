<script setup lang="ts">
import { computed } from 'vue'
import { getSlotRegistrations } from '@/core/plugin-registry'
import type { SlotRegistration } from '@/core/types'

const props = defineProps<{
  panelId: string | null
  title?: string
}>()

const panels = computed(() => getSlotRegistrations('sidebar:panel'))

const activePanel = computed<SlotRegistration | undefined>(() =>
  panels.value.find(p => p.panelId === props.panelId),
)

const panelTitle = computed(() => {
  if (props.title) return props.title
  return activePanel.value?.panelLabel ?? activePanel.value?.id ?? ''
})
</script>

<template>
  <div v-if="panelId" class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">{{ panelTitle }}</span>
      <slot name="header-actions" />
    </div>
    <div class="sidebar-content">
      <slot>
        <component :is="activePanel?.component" v-bind="$attrs" />
      </slot>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 36px;
}

.sidebar-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}
</style>
