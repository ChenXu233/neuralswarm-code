<script setup lang="ts">
import { Puzzle } from 'lucide-vue-next'
</script>

<template>
  <div class="plugins-panel">
    <div class="empty-state">
      <Puzzle />
      <p>{{ $t('plugins.noPlugins') }}</p>
    </div>
  </div>
</template>

<style scoped>
.plugins-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
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
  font-size: var(--text-sm);
}

.empty-state .lucide {
  width: 2rem;
  height: 2rem;
}
</style>
