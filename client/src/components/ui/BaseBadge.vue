<script setup lang="ts">
defineProps<{
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error'
}>()
</script>

<template>
  <span :class="['badge', variant || 'default']">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 500;
}

.default {
  background-color: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.primary {
  background-color: #e6f7ff;
  color: var(--color-accent);
}

.success {
  background-color: #f6ffed;
  color: var(--color-success);
}

.warning {
  background-color: #fff7e6;
  color: var(--color-warning);
}

.error {
  background-color: #fff2f0;
  color: var(--color-error);
}
</style>