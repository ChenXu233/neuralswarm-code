<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">{{ title }}</span>
      <slot name="header-actions" />
    </div>
    <div class="sidebar-content">
      <slot />
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
