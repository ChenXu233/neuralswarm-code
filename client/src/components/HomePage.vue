<script setup lang="ts">
import { ref } from 'vue'
import { Folder, Plus, MessageSquare, ArrowLeft, Globe } from 'lucide-vue-next'
import type { Project } from '../api/client'
import { canOpenLocalFolder } from '../utils/platform'

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

  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}
</script>

<template>
  <div class="home-page">
    <div class="content-wrapper">
      <!-- Left: Brand -->
      <div class="brand-section">
        <div class="logo">N</div>
        <h1 class="brand-name">NeuralSwarm</h1>
        <p class="brand-desc">AI-Powered Development</p>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Right: Content -->
      <div class="action-section">
        <Transition name="slide-fade" mode="out-in">
          <!-- Projects list -->
          <div v-if="!showOptions" key="projects" class="projects-content">
            <div class="section-label">RECENT</div>
            <div class="project-list">
              <div
                v-for="project in projects"
                :key="project.id"
                class="project-item"
                @click="emit('select', project)"
              >
                <Folder :size="14" />
                <span class="project-path">{{ project.name }}</span>
                <span class="project-time">{{ formatTime(project.updated_at) }}</span>
              </div>
              <div v-if="projects.length === 0" class="empty-hint">
                No recent projects
              </div>
            </div>
            <button class="open-btn" @click="showOptions = true">
              Open...
            </button>
          </div>

          <!-- Options page -->
          <div v-else key="options" class="options-content">
            <div class="section-label">START A SESSION</div>
            <div class="options-list">
              <div v-if="canOpenLocalFolder()" class="option-item">
                <Folder :size="16" />
                <div class="option-info">
                  <div class="option-title">Open Folder</div>
                  <div class="option-desc">Browse a local directory</div>
                </div>
                <span class="option-shortcut">Ctrl+O</span>
              </div>
              <div v-else class="option-item">
                <Globe :size="16" />
                <div class="option-info">
                  <div class="option-title">Connect Cloud</div>
                  <div class="option-desc">Link a cloud project</div>
                </div>
              </div>
              <div class="option-item">
                <Plus :size="16" />
                <div class="option-info">
                  <div class="option-title">New Project</div>
                  <div class="option-desc">Start from scratch</div>
                </div>
                <span class="option-shortcut">Ctrl+N</span>
              </div>
              <div class="option-item accent" @click="emit('global')">
                <MessageSquare :size="16" />
                <div class="option-info">
                  <div class="option-title">Global Mode</div>
                  <div class="option-desc">No project context</div>
                </div>
                <span class="option-shortcut">Ctrl+G</span>
              </div>
            </div>
            <button class="back-link" @click="showOptions = false">
              <ArrowLeft :size="12" />
              Back
            </button>
          </div>
        </Transition>
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
  padding: 48px;
}

.content-wrapper {
  display: flex;
  align-items: center;
  gap: 56px;
}

/* --- Brand (Left) --- */
.brand-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
  min-width: 160px;
}

.logo {
  width: 48px;
  height: 48px;
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg);
  font-size: 22px;
  font-weight: var(--font-semibold);
  margin-bottom: 12px;
}

.brand-name {
  font-size: var(--text-xl);
  font-weight: var(--font-medium);
  color: var(--color-text);
  margin-bottom: 2px;
  line-height: 1.2;
}

.brand-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

/* --- Divider --- */
.divider {
  width: 1px;
  height: 140px;
  background: var(--color-border);
  flex-shrink: 0;
}

/* --- Action (Right) --- */
.action-section {
  min-width: 260px;
}

.section-label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.projects-content,
.options-content {
  width: 100%;
}

/* --- Project List --- */
.project-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 16px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.project-item:hover {
  background: var(--color-surface-hover);
}

.project-path {
  font-size: var(--text-sm);
  color: var(--color-text);
  flex: 1;
}

.project-time {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.empty-hint {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  padding: 8px;
}

/* --- Open Button --- */
.open-btn {
  padding: 6px 14px;
  background: var(--color-primary);
  color: var(--color-bg);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: background-color var(--transition-fast);
}

.open-btn:hover {
  background: var(--color-primary-hover);
}

/* --- Options --- */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 20px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.option-item:hover {
  background: var(--color-surface-hover);
}

.option-item.accent {
  background: color-mix(in srgb, var(--color-accent) 5%, transparent);
}

.option-item.accent:hover {
  background: color-mix(in srgb, var(--color-accent) 10%, transparent);
}

.option-item.accent .option-title {
  color: var(--color-accent);
}

.option-info {
  flex: 1;
}

.option-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.option-desc {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 1px;
}

.option-shortcut {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

/* --- Back Link --- */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

/* --- Responsive --- */
@media (max-width: 640px) {
  .content-wrapper {
    flex-direction: column;
    gap: 28px;
  }
  .brand-section {
    align-items: center;
    text-align: center;
  }
  .divider {
    width: 80px;
    height: 1px;
  }
}
</style>
