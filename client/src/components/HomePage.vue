<script setup lang="ts">
import { ref } from 'vue'
import { Folder, Plus, MessageSquare, ArrowLeft } from 'lucide-vue-next'
import type { Project } from '../api/client'

defineProps<{
  projects: Project[]
}>()

const emit = defineEmits<{
  select: [project: Project]
  global: []
}>()

const showOptions = ref(false)

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(hours / 24)

  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}
</script>

<template>
  <div class="home-page">
    <div class="content-wrapper">
      <!-- Left: Brand -->
      <div class="brand-section">
        <div class="logo">N</div>
        <h1 class="brand-name">NeuralSwarm</h1>
        <p class="brand-desc">选择一个项目开始，<br>或创建新项目</p>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Right: Projects or Options -->
      <div class="projects-section">
        <template v-if="!showOptions">
          <div class="section-label">最近项目</div>
          <div class="project-list">
            <div
              v-for="project in projects"
              :key="project.id"
              class="project-item"
              @click="emit('select', project)"
            >
              <Folder :size="14" />
              <span class="project-name">{{ project.name }}</span>
              <span class="project-time">{{ formatTime(project.updated_at) }}</span>
            </div>
          </div>
          <button class="open-btn" @click="showOptions = true">
            <Plus :size="12" />
            <span>打开项目</span>
          </button>
        </template>

        <template v-else>
          <div class="options-header">
            <button class="back-btn" @click="showOptions = false">
              <ArrowLeft :size="10" />
            </button>
            <span class="options-title">打开项目</span>
          </div>
          <div class="options-list">
            <div class="option-item">
              <Plus :size="16" color="#1890ff" />
              <div>
                <div class="option-title">新建项目</div>
                <div class="option-desc">创建一个新的工作空间</div>
              </div>
            </div>
            <div class="option-item">
              <Folder :size="16" color="#52c41a" />
              <div>
                <div class="option-title">打开文件夹</div>
                <div class="option-desc">从本地文件夹导入</div>
              </div>
            </div>
            <div class="option-item" @click="emit('global')">
              <MessageSquare :size="16" color="#faad14" />
              <div>
                <div class="option-title">全局模式</div>
                <div class="option-desc">不绑定项目，直接对话</div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.content-wrapper {
  display: flex;
  align-items: center;
  gap: 40px;
  max-width: 600px;
  width: 100%;
}

.brand-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 140px;
  padding: 20px;
}

.logo {
  width: 44px;
  height: 44px;
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 12px;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.brand-desc {
  font-size: 11px;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

.divider {
  width: 1px;
  height: 160px;
  background: var(--color-border);
  align-self: center;
}

.projects-section {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.section-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 14px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-text-secondary);
}

.project-item:hover {
  background: var(--color-surface-hover);
}

.project-name {
  font-size: 12px;
  color: var(--color-text);
  flex: 1;
}

.project-time {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.open-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
}

.open-btn:hover {
  background: var(--color-primary-hover);
}

.options-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.back-btn {
  padding: 3px 6px;
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--color-text-secondary);
}

.back-btn:hover {
  background: var(--color-border);
}

.options-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  cursor: pointer;
}

.option-item:hover .option-title {
  color: var(--color-accent);
}

.option-title {
  font-size: 12px;
  color: var(--color-text);
  font-weight: 500;
  transition: color var(--transition-fast);
}

.option-desc {
  font-size: 11px;
  color: var(--color-text-tertiary);
}
</style>
