<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from './composables/useTheme'
import HomePage from './components/HomePage.vue'
import TaskView from './views/TaskView.vue'
import { listProjects, type Project } from './api/client'

// 初始化主题
useTheme()

const selectedProject = ref<Project | null>(null)
const projects = ref<Project[]>([])

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
  <div id="app">
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
</template>

<style>
/* Global styles are in base.css */
</style>
