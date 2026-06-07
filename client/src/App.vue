<script setup lang="ts">
import { ref } from 'vue'
import ProjectView from './views/ProjectView.vue'
import TaskView from './views/TaskView.vue'
import type { Project } from './api/client'

const selectedProject = ref<Project | null>(null)
</script>

<template>
  <div id="app">
    <ProjectView v-if="!selectedProject" @select="selectedProject = $event" />
    <TaskView v-else :project="selectedProject" @back="selectedProject = null" />
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
#app { height: 100vh; }
</style>
