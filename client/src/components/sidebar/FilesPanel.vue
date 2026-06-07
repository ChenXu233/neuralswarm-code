<script setup lang="ts">
import { Folder } from 'lucide-vue-next'

defineProps<{
  hasOpenProject?: boolean
}>()
</script>

<template>
  <div class="files-panel">
    <div class="panel-header">
      <span class="panel-title">EXPLORER</span>
    </div>

    <div v-if="hasOpenProject" class="file-tree">
      <!-- File tree will be populated from real data -->
    </div>

    <div v-else class="empty-state">
      <Folder :size="24" />
      <p class="empty-title">No project open</p>
      <p class="empty-desc">Open a project to browse its files,<br/>or start a global chat.</p>
    </div>
  </div>
</template>

<style scoped>
.files-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.file-tree {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 8px;
  padding: 24px;
  text-align: center;
}

.empty-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.empty-desc {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  line-height: 1.5;
}
</style>
