<script setup lang="ts">
import { Puzzle } from 'lucide-vue-next'
</script>

<template>
  <div class="plugins-panel">
    <div class="panel-header">
      <span class="panel-title">插件</span>
    </div>
    <div class="empty-state">
      <Puzzle :size="32" />
      <p>暂无插件</p>
    </div>
  </div>
</template>

<style scoped>
.plugins-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 8px;
}

.empty-state p {
  font-size: 12px;
}
</style>
