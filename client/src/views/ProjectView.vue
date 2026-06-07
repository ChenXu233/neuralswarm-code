<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listProjects, createProject, type Project } from '../api/client'

const emit = defineEmits<{ select: [project: Project] }>()
const projects = ref<Project[]>([])
const newName = ref('')
const newPath = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try { projects.value = await listProjects() } finally { loading.value = false }
}

async function create() {
  if (!newName.value || !newPath.value) return
  const p = await createProject(newName.value, newPath.value)
  projects.value.unshift(p)
  newName.value = ''
  newPath.value = ''
}

onMounted(load)
</script>

<template>
  <div class="project-view">
    <h2>Projects</h2>
    <div class="create-form">
      <input v-model="newName" placeholder="Project name" />
      <input v-model="newPath" placeholder="/path/to/project" />
      <button @click="create">Open Folder</button>
    </div>
    <div v-if="loading">Loading...</div>
    <div class="project-list">
      <div v-for="p in projects" :key="p.id" class="project-card" @click="emit('select', p)">
        <div class="name">{{ p.name }}</div>
        <div class="path">{{ p.path }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-view { padding: 20px; }
.create-form { display: flex; gap: 8px; margin-bottom: 20px; }
.create-form input { flex: 1; padding: 8px; border: 1px solid #d9d9d9; border-radius: 4px; }
.create-form button { padding: 8px 16px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.project-list { display: flex; flex-direction: column; gap: 8px; }
.project-card { padding: 16px; border: 1px solid #e8e8e8; border-radius: 8px; cursor: pointer; }
.project-card:hover { border-color: #1890ff; }
.name { font-weight: 500; }
.path { font-size: 12px; color: #999; margin-top: 4px; }
</style>
