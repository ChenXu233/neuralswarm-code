<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from './composables/useTheme'
import ActivityBar from './components/layout/ActivityBar.vue'
import HomePage from './components/HomePage.vue'
import TaskView from './views/TaskView.vue'
import { listProjects, type Project } from './api/client'

// 初始化主题
useTheme()

const selectedProject = ref<Project | null>(null)
const projects = ref<Project[]>([])
const activePanel = ref<'chat' | 'files' | 'plugins' | 'settings'>('chat')

// 加载项目列表
async function loadProjects() {
  try {
    projects.value = await listProjects()
  } catch (e) {
    console.error('Failed to load projects:', e)
  }
}

function handleSelectProject(project: Project) {
  selectedProject.value = project
}

function handleBack() {
  selectedProject.value = null
}

loadProjects()
</script>

<template>
  <div id="app" class="app-layout">
    <ActivityBar v-model:active-panel="activePanel" />
    <div class="app-content">
      <HomePage
        v-if="!selectedProject"
        :projects="projects"
        @select="handleSelectProject"
      />
      <TaskView
        v-else
        :project="selectedProject"
        :active-panel="activePanel"
        @back="handleBack"
        @update:active-panel="activePanel = $event"
      />
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
}

.app-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
