<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from './composables/useTheme'
import HomePage from './components/HomePage.vue'
import type { Project } from './api/client'

// 初始化主题
useTheme()

const selectedProject = ref<Project | null>(null)
const projects = ref<Project[]>([])

function handleSelectProject(project: Project) {
  selectedProject.value = project
}

function handleGlobalMode() {
  selectedProject.value = null
  // TODO: 进入全局模式对话
}
</script>

<template>
  <div id="app">
    <HomePage
      v-if="!selectedProject"
      :projects="projects"
      @select="handleSelectProject"
      @global="handleGlobalMode"
    />
    <!-- TODO: TaskView will be integrated in Task 9 -->
    <div v-else>
      <p>TaskView will be here</p>
    </div>
  </div>
</template>

<style>
/* Global styles are in base.css */
</style>
