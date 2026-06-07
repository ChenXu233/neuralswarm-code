<script setup lang="ts">
defineProps<{
  status: 'running' | 'completed' | 'failed' | 'pending' | 'connected' | 'disconnected'
}>()
</script>

<template>
  <span :class="['status-dot', status]"></span>
</template>

<style scoped>
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.running {
  background-color: var(--color-success);
  animation: pulse-dot 2s ease-in-out infinite;
}

.completed { background-color: var(--color-success); }
.failed { background-color: var(--color-error); }
.pending { background-color: var(--color-text-tertiary); }
.connected { background-color: var(--color-success); }
.disconnected { background-color: var(--color-text-tertiary); }
</style>
