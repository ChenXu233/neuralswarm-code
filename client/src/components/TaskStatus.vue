<script setup lang="ts">
defineProps<{ status: string }>()
</script>

<template>
  <span :class="['status', status]">{{ status }}</span>
</template>

<style scoped>
.status { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.pending { background: #f0f0f0; color: #666; }
.running { background: #e6f7ff; color: #1890ff; }
.completed { background: #f6ffed; color: #52c41a; }
.failed { background: #fff2f0; color: #ff4d4f; }
.cancelled { background: #f0f0f0; color: #999; }
</style>
