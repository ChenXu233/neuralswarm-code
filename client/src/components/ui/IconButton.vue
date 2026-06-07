<script setup lang="ts">
defineProps<{
  active?: boolean
  tooltip?: string
}>()

defineEmits<{
  click: []
}>()
</script>

<template>
  <button
    :class="['icon-button', { active }]"
    :title="tooltip"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<style scoped>
.icon-button {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  position: relative;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.icon-button:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.icon-button.active {
  color: var(--color-accent);
  background-color: var(--color-activity-active);
}
</style>
