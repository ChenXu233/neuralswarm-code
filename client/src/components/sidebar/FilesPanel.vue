<script setup lang="ts">
import { ref } from 'vue'
import { Folder, File, ChevronRight } from 'lucide-vue-next'

interface FileItem {
  name: string
  type: 'file' | 'folder'
  children?: FileItem[]
}

const workspaces = ref(['neuralswarm-core', 'api-server'])

const files = ref<FileItem[]>([
  { name: 'src', type: 'folder', children: [
    { name: 'main.ts', type: 'file' },
    { name: 'App.vue', type: 'file' },
  ]},
  { name: 'package.json', type: 'file' },
])

const expandedFolders = ref<Set<string>>(new Set(['src']))

function toggleFolder(name: string) {
  if (expandedFolders.value.has(name)) {
    expandedFolders.value.delete(name)
  } else {
    expandedFolders.value.add(name)
  }
}
</script>

<template>
  <div class="files-panel">
    <div class="panel-header">
      <span class="panel-title">EXPLORER</span>
    </div>

    <div class="workspace-section">
      <div
        v-for="ws in workspaces"
        :key="ws"
        class="workspace-item"
      >
        <Folder :size="12" />
        <span>{{ ws }}</span>
      </div>
    </div>

    <div class="file-tree">
      <template v-for="file in files" :key="file.name">
        <div
          :class="['file-item', file.type]"
          @click="file.type === 'folder' && toggleFolder(file.name)"
        >
          <ChevronRight
            v-if="file.type === 'folder'"
            :size="10"
            :class="['chevron', { expanded: expandedFolders.has(file.name) }]"
          />
          <Folder v-if="file.type === 'folder'" :size="14" />
          <File v-else :size="14" />
          <span>{{ file.name }}</span>
        </div>
        <div
          v-if="file.type === 'folder' && expandedFolders.has(file.name) && file.children"
          class="sub-items"
        >
          <div
            v-for="child in file.children"
            :key="child.name"
            class="file-item child"
          >
            <File :size="14" />
            <span>{{ child.name }}</span>
          </div>
        </div>
      </template>
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

.workspace-section {
  padding: 4px 8px 8px;
  border-bottom: 1px solid var(--color-border);
}

.workspace-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
}

.file-tree {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.file-item:hover {
  background: var(--color-surface-hover);
}

.file-item.child {
  padding-left: 24px;
}

.chevron {
  transition: transform var(--transition-fast);
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.chevron.expanded {
  transform: rotate(90deg);
}
</style>
