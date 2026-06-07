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
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text);
  opacity: 0.6;
  transition: opacity var(--transition-fast), background-color var(--transition-fast);
}

.icon-button:hover {
  opacity: 1;
  background-color: var(--color-surface-hover);
}

.icon-button.active {
  opacity: 1;
  background-color: var(--color-activity-active);
}
</style>