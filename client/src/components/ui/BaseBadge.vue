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
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1.5;
}

.default {
  background-color: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.primary {
  background-color: color-mix(in srgb, var(--color-accent) 12%, transparent);
  color: var(--color-accent);
}

.success {
  background-color: color-mix(in srgb, var(--color-success) 12%, transparent);
  color: var(--color-success);
}

.warning {
  background-color: color-mix(in srgb, var(--color-warning) 12%, transparent);
  color: var(--color-warning);
}

.error {
  background-color: color-mix(in srgb, var(--color-error) 12%, transparent);
  color: var(--color-error);
}
</style>
