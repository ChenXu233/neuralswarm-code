<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from './composables/useTheme'
import ActivityBar from './components/layout/ActivityBar.vue'
import Sidebar from './components/layout/Sidebar.vue'
import SettingsPanel from './components/sidebar/SettingsPanel.vue'
import HomePage from './components/HomePage.vue'
import TaskView from './views/TaskView.vue'
import { useTask } from './composables/useTask'
import { listProjects, type Project, type Task } from './api/client'
import { useI18n } from 'vue-i18n'
import ServerSetupDialog from './components/ServerSetupDialog.vue'
import { useServerConnection } from './composables/useServerConnection'

useI18n()
useTheme()

const selectedProject = ref<Project | null>(null)
const projects = ref<Project[]>([])
const activePanel = ref<string | null>('chat')
const showSettings = ref(false)

const { tasks, currentTask, loadTasks } = useTask()

const { hasConfiguredServers } = useServerConnection()
const showServerSetup = ref(false)

// 检查是否需要显示服务器设置对话框
function checkServerSetup() {
  if (!hasConfiguredServers.value) {
    showServerSetup.value = true
  }
}

// 处理服务器连接成功
function handleServerConnected() {
  showServerSetup.value = false
  // 重新加载项目列表
  loadProjects()
}

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

function handleToggleSettings() {
  showSettings.value = !showSettings.value
}

// 在组件挂载时检查
checkServerSetup()

loadProjects()
</script>

<template>
  <div id="app" class="app-layout">
    <!-- 服务器设置对话框 -->
    <ServerSetupDialog
      v-if="showServerSetup"
      @connected="handleServerConnected"
    />

    <ActivityBar
      v-model:active-panel="activePanel"
      :show-settings="showSettings"
      @toggle-settings="handleToggleSettings"
    />

    <!-- Sidebar: visible when a panel is active and settings is closed -->
    <Sidebar
      v-if="activePanel && !showSettings"
      :panel-id="activePanel"
      :tasks="tasks"
      :active-task-id="currentTask?.id"
      :has-open-project="!!selectedProject"
      :project-id="selectedProject?.id || ''"
      @select="handleSelectTask"
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

    <!-- Settings overlay -->
    <SettingsPanel v-if="showSettings" @close="showSettings = false" />
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
