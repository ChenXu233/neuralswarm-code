<template>
  <div class="memory-panel">
    <div class="panel-header">
      <span class="panel-title">{{ $t('memory.title') }}</span>
      <select v-model="selectedLevel" @change="loadMemory" class="level-select">
        <option value="L1">{{ $t('memory.l1Events') }}</option>
        <option value="L2">{{ $t('memory.l2Knowledge') }}</option>
        <option value="L3">{{ $t('memory.l3Preferences') }}</option>
      </select>
    </div>

    <div class="memory-content">
      <div v-if="loading" class="loading">{{ $t('memory.loading') }}</div>

      <div v-else-if="selectedLevel === 'L1'" class="event-list">
        <div v-for="(event, index) in memories" :key="index" class="event-item">
          <span class="event-type">{{ event.event }}</span>
          <span class="event-detail">{{ event.detail }}</span>
        </div>
        <div v-if="memories.length === 0" class="empty">{{ $t('memory.noEvents') }}</div>
      </div>

      <div v-else-if="selectedLevel === 'L2'" class="knowledge-list">
        <div v-for="(item, index) in memories" :key="index" class="knowledge-item">
          <div class="knowledge-content">{{ item.content }}</div>
          <div class="knowledge-source">{{ $t('memory.source', { source: item.source }) }}</div>
        </div>
        <div v-if="memories.length === 0" class="empty">{{ $t('memory.noKnowledge') }}</div>
      </div>

      <div v-else-if="selectedLevel === 'L3'" class="preference-list">
        <div v-if="memories.length === 0" class="empty">{{ $t('memory.noPreferences') }}</div>
      </div>
    </div>

    <div class="panel-footer">
      <button @click="loadMemory" :disabled="loading" class="refresh-btn">{{ $t('memory.refresh') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMemory } from '@/api/client'

const props = defineProps<{
  projectId: string
}>()

const selectedLevel = ref('L1')
const memories = ref<any[]>([])
const loading = ref(false)

async function loadMemory() {
  if (!props.projectId) return

  loading.value = true
  try {
    const result = await getMemory(props.projectId, selectedLevel.value)
    memories.value = result.data || []
  } catch (error) {
    console.error('Failed to load memory:', error)
    memories.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMemory()
})
</script>

<style scoped>
.memory-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.level-select {
  padding: 4px 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

.level-select:focus {
  outline: none;
  border-color: var(--color-text-tertiary);
}

.memory-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.loading,
.empty {
  text-align: center;
  padding: 20px;
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
}

.event-list,
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-item,
.knowledge-item {
  padding: 8px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.event-type {
  font-weight: var(--font-medium);
  margin-right: 8px;
  color: var(--color-text);
}

.event-detail {
  color: var(--color-text-secondary);
}

.knowledge-content {
  margin-bottom: 4px;
  color: var(--color-text);
}

.knowledge-source {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.panel-footer {
  padding: 8px 12px;
  text-align: right;
}

.refresh-btn {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text);
  transition: background-color var(--transition-fast);
}

.refresh-btn:hover {
  background: var(--color-surface-hover);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
