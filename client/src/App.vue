<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from './composables/useTheme'
import ActivityBar from './components/layout/ActivityBar.vue'
import Sidebar from './components/layout/Sidebar.vue'
import ChatPanel from './components/sidebar/ChatPanel.vue'
import FilesPanel from './components/sidebar/FilesPanel.vue'
import PluginsPanel from './components/sidebar/PluginsPanel.vue'
import SettingsPanel from './components/sidebar/SettingsPanel.vue'
import MemoryPanel from './components/sidebar/MemoryPanel.vue'
import HomePage from './components/HomePage.vue'
import TaskView from './views/TaskView.vue'
import { useTask } from './composables/useTask'
import { listProjects, type Project, type Task } from './api/client'

useTheme()

const selectedProject = ref<Project | null>(null)
const projects = ref<Project[]>([])
const activePanel = ref<'chat' | 'files' | 'plugins' | 'memory' | 'settings' | null>('chat')

const { tasks, currentTask, loadTasks } = useTask()

function handleSelectTask(task: Task) {
  currentTask.value = task
}

async function loadProjects() {
  try {
    projects.value = await listProjects()
  } catch (e) {
    console.error('Failed to load projects:', e)
  }
}

function handleSelectProject(project: Project) {
  selectedProject.value = project
  loadTasks(project.id)
}

function handleBack() {
  selectedProject.value = null
}

loadProjects()
</script>

<template>
  <div id="app" class="app-layout">
    <ActivityBar v-model:active-panel="activePanel" />

    <!-- Shared sidebar: visible when any panel is active, regardless of page -->
    <Sidebar
      v-if="activePanel && activePanel !== 'settings'"
      :title="activePanel === 'chat' ? 'Chat' : activePanel === 'files' ? 'Files' : activePanel === 'plugins' ? 'Plugins' : 'Memory'"
    >
      <ChatPanel
        v-if="activePanel === 'chat'"
        :tasks="tasks"
        :active-task-id="currentTask?.id"
        @select="handleSelectTask"
      />
      <FilesPanel v-else-if="activePanel === 'files'" :has-open-project="!!selectedProject" />
      <PluginsPanel v-else-if="activePanel === 'plugins'" />
      <MemoryPanel v-else-if="activePanel === 'memory'" :project-id="selectedProject?.id || ''" />
    </Sidebar>

    <SettingsPanel
      v-else-if="activePanel === 'settings'"
      :servers="[]"
    />

    <div class="app-content">
      <HomePage
        v-if="!selectedProject"
        :projects="projects"
        @select="handleSelectProject"
      />
      <TaskView
        v-else
        :project="selectedProject"
        @back="handleBack"
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
