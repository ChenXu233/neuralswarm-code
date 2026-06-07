<script setup lang="ts">
import { ref } from 'vue'
import { Folder, File, ChevronRight } from 'lucide-vue-next'

interface FileItem {
  name: string
  type: 'file' | 'folder'
  children?: FileItem[]
}

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
      <span class="panel-title">文件</span>
    </div>
    <div class="file-tree">
      <template v-for="file in files" :key="file.name">
        <div
          :class="['file-item', file.type]"
          @click="file.type === 'folder' && toggleFolder(file.name)"
        >
          <ChevronRight
            v-if="file.type === 'folder'"
            :size="12"
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
            class="file-item"
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

.file-tree {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text);
}

.file-item:hover {
  background: var(--color-surface-hover);
}

.chevron {
  transition: transform var(--transition-fast);
}

.chevron.expanded {
  transform: rotate(90deg);
}

.sub-items {
  padding-left: 16px;
}
</style>
