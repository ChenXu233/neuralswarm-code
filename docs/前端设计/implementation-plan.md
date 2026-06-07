# NeuralSwarm Client 前端重设计实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 NeuralSwarm Client 从当前 VS Code 风格 IDE 界面升级为 Editorial + Glassmorphism 设计语言，保持现有交互逻辑不变。

**Architecture:** 渐进式改造——从 CSS 变量基础设施开始，逐层向上替换 UI 原语、页面、组件。每一步独立可交付，不改动现有 Vue 3 Composition API 逻辑、WebSocket 连接、API 客户端。

**Tech Stack:** Vue 3.4 + TypeScript + Vite + lucide-vue-next + markdown-it

---

## 文件变更总览

| 操作 | 文件 |
|------|------|
| 重写 | `src/styles/variables.css` |
| 修改 | `src/styles/base.css` |
| 重写 | `src/styles/transitions.css` |
| 修改 | `src/components/ui/StatusDot.vue` |
| 修改 | `src/components/ui/IconButton.vue` |
| 修改 | `src/components/ui/BaseBadge.vue` |
| 重写 | `src/components/HomePage.vue` |
| 修改 | `src/components/layout/ActivityBar.vue` |
| 修改 | `src/components/layout/Sidebar.vue` |
| 修改 | `src/components/sidebar/ChatPanel.vue` |
| 修改 | `src/components/sidebar/FilesPanel.vue` |
| 修改 | `src/components/sidebar/PluginsPanel.vue` |
| 修改 | `src/components/sidebar/SettingsPanel.vue` |
| 重写 | `src/components/ChatMessage.vue` |
| 重写 | `src/components/ToolCall.vue` |
| **新建** | `src/components/chat/DiffView.vue` |
| 重写 | `src/components/chat/CodeBlock.vue` |
| 重写 | `src/components/chat/ChatInput.vue` |
| 修改 | `src/views/TaskView.vue` |
| 修改 | `src/App.vue` |

---

### Task 1: CSS 变量体系重写

**Files:**
- Modify: `src/styles/variables.css`

- [ ] **Step 1: 替换为完整 token 体系**

将 `src/styles/variables.css` 完整替换为：

```css
/* ========================================
   NeuralSwarm Design Token System v2
   ======================================== */

/* --- Warm Stone (默认) --- */
:root {
  /* 配色 */
  --color-bg: #faf8f5;
  --color-surface: #ffffff;
  --color-surface-hover: #f5f3f0;
  --color-activity-bg: rgba(240, 236, 230, 0.6);
  --color-activity-active: rgba(196, 117, 90, 0.08);
  --color-text: #2d2a26;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-border: #e8e4df;
  --color-primary: #2d2a26;
  --color-primary-hover: #1a1816;
  --color-accent: #c4755a;
  --color-accent-hover: #a8624a;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 14px;
  --radius-xl: 20px;
  --radius-full: 9999px;

  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.08);
  --shadow-glow: 0 0 12px rgba(196, 117, 90, 0.15);

  /* 字体 */
  --font-sans: system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;

  /* 字号刻度 */
  --text-xs: 10px;
  --text-sm: 12px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 20px;
  --text-2xl: 26px;
  --text-display: 36px;

  /* 动效 */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);

  /* 布局 */
  --activity-bar-width: 48px;
  --sidebar-width: 240px;
}

/* --- Dark Slate --- */
[data-theme="dark-slate"] {
  --color-bg: #1a1d23;
  --color-surface: #25282e;
  --color-surface-hover: #2a2d33;
  --color-activity-bg: rgba(34, 37, 43, 0.6);
  --color-activity-active: rgba(107, 140, 255, 0.1);
  --color-text: #e0e0e0;
  --color-text-secondary: #999999;
  --color-text-tertiary: #666666;
  --color-border: #2a2d33;
  --color-primary: #e0e0e0;
  --color-primary-hover: #ffffff;
  --color-accent: #6b8cff;
  --color-accent-hover: #8aa4ff;
  --color-success: #4ec9b0;
  --color-warning: #cca700;
  --color-error: #f44747;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.25);
  --shadow-glow: 0 0 12px rgba(107, 140, 255, 0.15);
}

/* --- Pure Minimal --- */
[data-theme="pure-minimal"] {
  --color-bg: #ffffff;
  --color-surface: #fafafa;
  --color-surface-hover: #f0f0f0;
  --color-activity-bg: rgba(245, 245, 245, 0.6);
  --color-activity-active: rgba(107, 154, 122, 0.08);
  --color-text: #111111;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-border: #eeeeee;
  --color-primary: #111111;
  --color-primary-hover: #000000;
  --color-accent: #6b9a7a;
  --color-accent-hover: #5a8a6a;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.06);
  --shadow-glow: 0 0 12px rgba(107, 154, 122, 0.12);
}

/* --- Amber Glow --- */
[data-theme="amber-glow"] {
  --color-bg: #0d0d0d;
  --color-surface: #141414;
  --color-surface-hover: #1a1a1a;
  --color-activity-bg: rgba(17, 17, 17, 0.6);
  --color-activity-active: rgba(255, 180, 50, 0.1);
  --color-text: #ffcc66;
  --color-text-secondary: #997744;
  --color-text-tertiary: #554433;
  --color-border: #222222;
  --color-primary: #ffcc66;
  --color-primary-hover: #ffddaa;
  --color-accent: #ffb432;
  --color-accent-hover: #ffc966;
  --color-success: #aacc44;
  --color-warning: #ffb432;
  --color-error: #ff6644;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.25);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.35);
  --shadow-glow: 0 0 12px rgba(255, 180, 50, 0.2);
}

/* --- 保留旧 dark 别名 (向后兼容) --- */
[data-theme="dark"] {
  --color-bg: #1a1d23;
  --color-surface: #25282e;
  --color-surface-hover: #2a2d33;
  --color-activity-bg: rgba(34, 37, 43, 0.6);
  --color-activity-active: rgba(107, 140, 255, 0.1);
  --color-text: #e0e0e0;
  --color-text-secondary: #999999;
  --color-text-tertiary: #666666;
  --color-border: #2a2d33;
  --color-primary: #e0e0e0;
  --color-primary-hover: #ffffff;
  --color-accent: #6b8cff;
  --color-accent-hover: #8aa4ff;
  --color-success: #4ec9b0;
  --color-warning: #cca700;
  --color-error: #f44747;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.25);
  --shadow-glow: 0 0 12px rgba(107, 140, 255, 0.15);
}
```

- [ ] **Step 2: 提交**

```bash
git add src/styles/variables.css
git commit -m "feat: rewrite CSS token system with 4 themes and glassmorphism support"
```

---

### Task 2: 基础样式 + 过渡动画适配

**Files:**
- Modify: `src/styles/base.css`
- Modify: `src/styles/transitions.css`

- [ ] **Step 1: 更新 base.css**

将 `src/styles/base.css` 中的 `body` 字号改为 14px（已为14px，无需改），添加毛玻璃工具类和流式光标动画：

```css
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100vh;
}

a {
  color: var(--color-accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* 毛玻璃工具类 */
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* 流式闪烁光标 */
@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.cursor-blink {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--color-text);
  vertical-align: text-bottom;
  margin-left: 2px;
  animation: blink-cursor 1s step-end infinite;
}

/* 呼吸动画 (StatusDot) */
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

/* 展开/折叠 */
@keyframes expand-in {
  from { max-height: 0; opacity: 0; }
  to { max-height: 2000px; opacity: 1; }
}

@keyframes collapse-out {
  from { max-height: 2000px; opacity: 1; }
  to { max-height: 0; opacity: 0; }
}

/* 消息入场 */
@keyframes message-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}
```

- [ ] **Step 2: 更新 transitions.css**

替换 `src/styles/transitions.css`，增加 slide-fade 作为全局过渡：

```css
/* 淡入 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑入 */
.slide-enter-active,
.slide-leave-active {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}
.slide-enter-from {
  transform: translateY(10px);
  opacity: 0;
}
.slide-leave-to {
  transform: translateY(10px);
  opacity: 0;
}

/* 缩放进入 */
.scale-enter-active,
.scale-leave-active {
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}
.scale-enter-from,
.scale-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

/* 首页 slide-fade (带方向) */
.slide-fade-enter-active {
  transition: all 0.25s var(--ease-out);
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

/* 展开/折叠 */
.expand-enter-active {
  animation: expand-in var(--transition-normal) var(--ease-out);
}
.expand-leave-active {
  animation: collapse-out var(--transition-fast) ease-in;
}

/* 消息入场 */
.message-enter-active {
  animation: message-in var(--transition-normal) var(--ease-out);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/styles/base.css src/styles/transitions.css
git commit -m "feat: add glass utility, cursor blink, expand animations, and message transitions"
```

---

### Task 3: UI 原语组件适配

**Files:**
- Modify: `src/components/ui/StatusDot.vue`
- Modify: `src/components/ui/IconButton.vue`
- Modify: `src/components/ui/BaseBadge.vue`

- [ ] **Step 1: StatusDot — 添加呼吸动画**

替换 `src/components/ui/StatusDot.vue`：

```vue
<script setup lang="ts">
defineProps<{
  status: 'running' | 'completed' | 'failed' | 'pending' | 'connected' | 'disconnected'
}>()
</script>

<template>
  <span :class="['status-dot', status]"></span>
</template>

<style scoped>
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.running {
  background-color: var(--color-success);
  animation: pulse-dot 2s ease-in-out infinite;
}

.completed { background-color: var(--color-success); }
.failed { background-color: var(--color-error); }
.pending { background-color: var(--color-text-tertiary); }
.connected { background-color: var(--color-success); }
.disconnected { background-color: var(--color-text-tertiary); }
</style>
```

- [ ] **Step 2: IconButton — 适配新圆角**

替换 `src/components/ui/IconButton.vue` 样式部分，尺寸改为 30×30px 适配 ActivityBar：

```vue
<script setup lang="ts">
defineProps<{
  active?: boolean
  tooltip?: string
}>()

defineEmits<{
  click: []
}>()
</script>

<template>
  <button
    :class="['icon-button', { active }]"
    :title="tooltip"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<style scoped>
.icon-button {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast), color var(--transition-fast);
  position: relative;
}

.icon-button:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.icon-button.active {
  color: var(--color-accent);
  background-color: var(--color-activity-active);
}
</style>
```

- [ ] **Step 3: BaseBadge — 适配新变量**

替换 `src/components/ui/BaseBadge.vue`，badge 色改用半透明变量背景：

```vue
<script setup lang="ts">
defineProps<{
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error'
}>()
</script>

<template>
  <span :class="['badge', variant || 'default']">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1.5;
}

.default {
  background-color: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.primary {
  background-color: color-mix(in srgb, var(--color-accent) 12%, transparent);
  color: var(--color-accent);
}

.success {
  background-color: color-mix(in srgb, var(--color-success) 12%, transparent);
  color: var(--color-success);
}

.warning {
  background-color: color-mix(in srgb, var(--color-warning) 12%, transparent);
  color: var(--color-warning);
}

.error {
  background-color: color-mix(in srgb, var(--color-error) 12%, transparent);
  color: var(--color-error);
}
</style>
```

- [ ] **Step 4: 提交**

```bash
git add src/components/ui/StatusDot.vue src/components/ui/IconButton.vue src/components/ui/BaseBadge.vue
git commit -m "feat: adapt UI primitives to new token system with pulse animation"
```

---

### Task 4: 首页重写 — VS Code 风格

**Files:**
- Modify: `src/components/HomePage.vue`

- [ ] **Step 1: 重写 HomePage.vue**

完整替换 `src/components/HomePage.vue`：

```vue
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

function formatTime(dateStr: string): string {
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
              <div class="option-item">
                <Folder :size="16" />
                <div class="option-info">
                  <div class="option-title">Open Folder</div>
                  <div class="option-desc">Browse a local directory</div>
                </div>
                <span class="option-shortcut">Ctrl+O</span>
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
```

- [ ] **Step 2: 提交**

```bash
git add src/components/HomePage.vue
git commit -m "feat: redesign homepage with VS Code-style two-column layout"
```

---

### Task 5: ActivityBar — 毛玻璃 + 选中指示线

**Files:**
- Modify: `src/components/layout/ActivityBar.vue`

- [ ] **Step 1: 替换 ActivityBar.vue 样式**

修改 `src/components/layout/ActivityBar.vue`，增加 Logo 和选中态指示线：

```vue
<script setup lang="ts">
import { MessageSquare, Folder, Puzzle, Settings } from 'lucide-vue-next'

defineProps<{
  activePanel: 'chat' | 'files' | 'plugins' | 'settings'
}>()

defineEmits<{
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings']
}>()
</script>

<template>
  <div class="activity-bar">
    <!-- Logo -->
    <div class="activity-logo">N</div>

    <div class="top-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'chat' }]"
        title="Chat"
        @click="$emit('update:activePanel', 'chat')"
      >
        <MessageSquare :size="16" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'files' }]"
        title="Files"
        @click="$emit('update:activePanel', 'files')"
      >
        <Folder :size="16" />
      </button>
      <button
        :class="['activity-btn', { active: activePanel === 'plugins' }]"
        title="Plugins"
        @click="$emit('update:activePanel', 'plugins')"
      >
        <Puzzle :size="16" />
      </button>
    </div>

    <div class="bottom-icons">
      <button
        :class="['activity-btn', { active: activePanel === 'settings' }]"
        title="Settings"
        @click="$emit('update:activePanel', 'settings')"
      >
        <Settings :size="16" />
        <span class="connection-dot"></span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.activity-bar {
  width: var(--activity-bar-width);
  background: var(--color-activity-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  gap: 6px;
}

/* Logo */
.activity-logo {
  width: 32px;
  height: 32px;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg);
  font-size: 14px;
  font-weight: var(--font-semibold);
  margin-bottom: 10px;
}

.top-icons, .bottom-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.top-icons {
  flex: 1;
}

.bottom-icons {
  position: relative;
}

/* Activity Button */
.activity-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  position: relative;
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.activity-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-surface-hover);
}

/* Active: left indicator line */
.activity-btn.active {
  color: var(--color-accent);
  background: var(--color-activity-active);
}

.activity-btn.active::before {
  content: '';
  position: absolute;
  left: -9px;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: var(--color-accent);
  border-radius: 0 2px 2px 0;
}

/* Connection dot */
.connection-dot {
  position: absolute;
  right: 2px;
  bottom: 2px;
  width: 7px;
  height: 7px;
  background-color: var(--color-success);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-activity-bg);
}
</style>
```

- [ ] **Step 2: 移除 IconButton 依赖**

不再从 `IconButton.vue` 导入——ActivityBar 现在使用自己的 `activity-btn` 样式。

- [ ] **Step 3: 提交**

```bash
git add src/components/layout/ActivityBar.vue
git commit -m "feat: add glassmorphism and left-indicator to ActivityBar"
```

---

### Task 6: Sidebar + ChatPanel 精细化

**Files:**
- Modify: `src/components/layout/Sidebar.vue`
- Modify: `src/components/sidebar/ChatPanel.vue`

- [ ] **Step 1: Sidebar — 更新样式为新变量**

替换 `src/components/layout/Sidebar.vue` 样式：

```vue
<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">{{ title }}</span>
      <slot name="header-actions" />
    </div>
    <div class="sidebar-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 36px;
}

.sidebar-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}
</style>
```

- [ ] **Step 2: ChatPanel — 改进搜索框样式、选中态**

替换 `src/components/sidebar/ChatPanel.vue` 样式部分：

```vue
<script setup lang="ts">
import { Search, Plus } from 'lucide-vue-next'
import StatusDot from '../ui/StatusDot.vue'
import type { Task } from '../../api/client'

defineProps<{
  tasks: Task[]
  activeTaskId?: string
}>()

defineEmits<{
  select: [task: Task]
  create: []
}>()

function getStatusVariant(status: string) {
  switch (status) {
    case 'running': return 'running'
    case 'completed': return 'completed'
    case 'failed': return 'failed'
    default: return 'pending'
  }
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}
</script>

<template>
  <div class="chat-panel">
    <!-- Header: title + add button -->
    <div class="panel-header">
      <span class="panel-title">TASKS</span>
      <button class="add-btn" @click="$emit('create')">
        <Plus :size="14" />
      </button>
    </div>

    <!-- Search -->
    <div class="search-box">
      <Search :size="12" />
      <input placeholder="Filter tasks..." />
    </div>

    <!-- Task list -->
    <div class="task-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        :class="['task-item', { active: task.id === activeTaskId }]"
        @click="$emit('select', task)"
      >
        <div class="task-header">
          <StatusDot :status="getStatusVariant(task.status)" />
          <span class="task-title">{{ task.input.slice(0, 40) }}</span>
        </div>
        <div class="task-meta">
          <span class="task-status">{{ task.status }}</span>
          <span class="task-time">{{ formatTime(task.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.add-btn {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.add-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.search-box {
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-surface-hover);
  margin: 0 8px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  color: var(--color-text-tertiary);
  transition: border-color var(--transition-fast);
}

.search-box:focus-within {
  border-color: var(--color-border);
}

.search-box input {
  border: none;
  background: transparent;
  font-size: var(--text-xs);
  color: var(--color-text);
  outline: none;
  width: 100%;
}

.search-box input::placeholder {
  color: var(--color-text-tertiary);
}

.task-list {
  flex: 1;
  overflow-y: auto;
}

.task-item {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: var(--radius-md);
  margin: 0 4px 2px;
  transition: background-color var(--transition-fast);
}

.task-item:hover {
  background: var(--color-surface-hover);
}

.task-item.active {
  background: var(--color-activity-active);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}

.task-title {
  font-size: var(--text-sm);
  color: var(--color-text);
  font-weight: var(--font-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-left: 14px;
}

.task-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.task-time {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
git add src/components/layout/Sidebar.vue src/components/sidebar/ChatPanel.vue
git commit -m "feat: refine Sidebar and ChatPanel with new tokens and task header"
```

---

### Task 7: FilesPanel + PluginsPanel + SettingsPanel 精细化

**Files:**
- Modify: `src/components/sidebar/FilesPanel.vue`
- Modify: `src/components/sidebar/PluginsPanel.vue`
- Modify: `src/components/sidebar/SettingsPanel.vue`

- [ ] **Step 1: FilesPanel — 工作区头部 + 改进文件树**

替换 `src/components/sidebar/FilesPanel.vue`：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { Folder, File, ChevronRight } from 'lucide-vue-next'

interface FileItem {
  name: string
  type: 'file' | 'folder'
  children?: FileItem[]
}

const workspaces = ref(['neuralswarm-core', 'api-server'])

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
    <!-- Header: EXPLORER title -->
    <div class="panel-header">
      <span class="panel-title">EXPLORER</span>
    </div>

    <!-- Workspace folders -->
    <div class="workspace-section">
      <div
        v-for="ws in workspaces"
        :key="ws"
        class="workspace-item"
      >
        <Folder :size="12" />
        <span>{{ ws }}</span>
      </div>
    </div>

    <!-- File tree -->
    <div class="file-tree">
      <template v-for="file in files" :key="file.name">
        <div
          :class="['file-item', file.type]"
          @click="file.type === 'folder' && toggleFolder(file.name)"
        >
          <ChevronRight
            v-if="file.type === 'folder'"
            :size="10"
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
            class="file-item child"
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
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.workspace-section {
  padding: 4px 8px 8px;
  border-bottom: 1px solid var(--color-border);
}

.workspace-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
}

.file-tree {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.file-item:hover {
  background: var(--color-surface-hover);
}

.file-item.child {
  padding-left: 24px;
}

.chevron {
  transition: transform var(--transition-fast);
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.chevron.expanded {
  transform: rotate(90deg);
}

.sub-items {
  /* no extra padding — handled by .child */
}
</style>
```

- [ ] **Step 2: PluginsPanel — 适配新变量**

替换 `src/components/sidebar/PluginsPanel.vue` 样式：

```vue
<style scoped>
.plugins-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 8px;
}

.empty-state p {
  font-size: var(--text-sm);
}
</style>
```

（script 和 template 保持不变）

- [ ] **Step 3: SettingsPanel — 增加主题切换**

替换 `src/components/sidebar/SettingsPanel.vue`：

```vue
<script setup lang="ts">
import StatusDot from '../ui/StatusDot.vue'
import { useTheme } from '../../composables/useTheme'

interface Server {
  url: string
  status: 'connected' | 'disconnected'
}

defineProps<{
  servers: Server[]
  activeServer?: string
}>()

defineEmits<{
  select: [server: Server]
}>()

const { theme, setTheme } = useTheme()

const themes = [
  { value: 'warm-stone', label: 'Warm Stone' },
  { value: 'dark-slate', label: 'Dark Slate' },
  { value: 'pure-minimal', label: 'Pure Minimal' },
  { value: 'amber-glow', label: 'Amber Glow' },
]
</script>

<template>
  <div class="settings-panel">
    <div class="panel-header">
      <span class="panel-title">SETTINGS</span>
    </div>

    <div class="settings-content">
      <!-- Servers -->
      <div class="section">
        <div class="section-label">SERVERS</div>
        <div
          v-for="server in servers"
          :key="server.url"
          :class="['setting-item', { active: server.url === activeServer }]"
          @click="$emit('select', server)"
        >
          <StatusDot :status="server.status" />
          <span class="item-label">{{ server.url }}</span>
          <span class="item-hint">{{ server.status === 'connected' ? 'connected' : 'offline' }}</span>
        </div>
        <button class="add-link">+ Add Server</button>
      </div>

      <!-- Theme -->
      <div class="section">
        <div class="section-label">THEME</div>
        <div
          v-for="t in themes"
          :key="t.value"
          :class="['setting-item', { active: theme === t.value }]"
          @click="setTheme(t.value)"
        >
          <span class="item-label">{{ t.label }}</span>
        </div>
      </div>

      <!-- Font -->
      <div class="section">
        <div class="section-label">FONT</div>
        <div class="font-input">
          <input placeholder="Custom font stack..." spellcheck="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 8px 12px;
}

.panel-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.section {
  margin-bottom: 16px;
}

.section-label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  font-weight: var(--font-semibold);
  letter-spacing: 1px;
  margin-bottom: 4px;
  padding: 0 8px;
}

.setting-item {
  padding: 6px 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: background-color var(--transition-fast);
}

.setting-item:hover {
  background: var(--color-surface-hover);
}

.setting-item.active {
  background: var(--color-activity-active);
  color: var(--color-accent);
}

.item-label {
  flex: 1;
  font-size: var(--text-sm);
}

.item-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.add-link {
  padding: 5px 8px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  width: 100%;
  margin-top: 2px;
  transition: border-color var(--transition-fast), color var(--transition-fast);
}

.add-link:hover {
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

.font-input {
  padding: 0 8px;
}

.font-input input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  font-size: var(--text-xs);
  color: var(--color-text);
  outline: none;
  font-family: var(--font-mono);
}

.font-input input:focus {
  border-color: var(--color-accent);
}
</style>
```

- [ ] **Step 4: 更新 useTheme.ts 支持四套主题**

修改 `src/composables/useTheme.ts`，使 `setTheme` 接受新主题值，并导出当前 `theme`：

```typescript
import { ref } from 'vue'

type Theme = 'warm-stone' | 'dark-slate' | 'pure-minimal' | 'amber-glow'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'warm-stone')

export function useTheme() {
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.dataset.theme = newTheme
  }

  // Initialize on first call
  document.documentElement.dataset.theme = theme.value

  return { theme, setTheme }
}
```

- [ ] **Step 5: 提交**

```bash
git add src/components/sidebar/FilesPanel.vue src/components/sidebar/PluginsPanel.vue src/components/sidebar/SettingsPanel.vue src/composables/useTheme.ts
git commit -m "feat: refine Files/Plugins/Settings panels with workspace header and theme switcher"
```

---

### Task 8: ChatMessage — 去卡片化 + Thinking 支持

**Files:**
- Modify: `src/components/ChatMessage.vue`

- [ ] **Step 1: 重写 ChatMessage.vue**

完整替换 `src/components/ChatMessage.vue`，增加 Thinking 折叠区和流式光标支持：

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown, Pencil } from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  thinkingDone?: boolean
  streaming?: boolean
}>()

const emit = defineEmits<{
  edit: []
}>()

const md = new MarkdownIt()
const html = computed(() => md.render(props.content))
const thinkingExpanded = ref(false)
const showEdit = ref(false)

function toggleThinking() {
  thinkingExpanded.value = !thinkingExpanded.value
}
</script>

<template>
  <div :class="['message', role]">
    <!-- Thinking section -->
    <div v-if="thinking || (streaming && role === 'assistant')" class="thinking-section">
      <div
        :class="['thinking-toggle', { expanded: thinkingExpanded }]"
        @click="toggleThinking"
      >
        <ChevronRight v-if="!thinkingExpanded" :size="12" class="chevron" />
        <ChevronDown v-else :size="12" class="chevron" />
        <span class="thinking-label">Thinking</span>
        <span v-if="thinkingDone" class="thinking-duration">· done</span>
        <span v-else class="thinking-duration">· ...</span>
      </div>
      <Transition name="expand">
        <div v-if="thinkingExpanded || (streaming && !thinkingDone)" class="thinking-content">
          {{ thinking || '' }}
          <span v-if="streaming && !thinkingDone" class="cursor-blink"></span>
        </div>
      </Transition>
    </div>

    <!-- User message: right aligned, filled -->
    <div
      v-if="role === 'user'"
      class="user-wrapper"
      @mouseenter="showEdit = true"
      @mouseleave="showEdit = false"
    >
      <button v-if="showEdit" class="edit-btn" @click="emit('edit')" title="Edit message">
        <Pencil :size="14" />
      </button>
      <div class="user-content">
        {{ content }}
      </div>
    </div>

    <!-- Assistant message: left aligned, no bubble -->
    <div v-else class="assistant-content" v-html="html">
    </div>

    <!-- Streaming cursor (assistant content) -->
    <span v-if="streaming && role === 'assistant'" class="cursor-blink"></span>
  </div>
</template>

<style scoped>
.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  animation: message-in var(--transition-normal) var(--ease-out);
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

/* --- Thinking --- */
.thinking-section {
  margin-bottom: 8px;
  width: 100%;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  transition: background-color var(--transition-fast);
  user-select: none;
}

.thinking-toggle:hover {
  background: var(--color-surface-hover);
}

.thinking-label {
  font-weight: var(--font-medium);
}

.thinking-duration {
  color: var(--color-text-tertiary);
}

.chevron {
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.thinking-content {
  margin-top: 4px;
  padding: 6px 12px;
  border-left: 2px solid var(--color-border);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  line-height: 1.7;
  white-space: pre-wrap;
  overflow: hidden;
}

/* --- User --- */
.user-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  max-width: 75%;
}

.user-content {
  background: var(--color-primary);
  color: var(--color-bg);
  padding: 10px 14px;
  border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
  font-size: var(--text-base);
  line-height: 1.5;
  box-shadow: var(--shadow-sm);
}

.edit-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast), background-color var(--transition-fast);
}

.user-wrapper:hover .edit-btn {
  opacity: 1;
}

.edit-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

/* --- Assistant --- */
.assistant-content {
  max-width: 80%;
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--color-text);
}

/* Deep styles for markdown */
.assistant-content :deep(p) {
  margin-bottom: 8px;
}

.assistant-content :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-content :deep(ul), .assistant-content :deep(ol) {
  margin-bottom: 8px;
  padding-left: 20px;
}

.assistant-content :deep(li) {
  margin-bottom: 2px;
}

.assistant-content :deep(code) {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--color-surface-hover);
  padding: 1px 5px;
  border-radius: 3px;
}

.assistant-content :deep(pre) {
  background: #1e1e1e;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 8px 0;
}

.assistant-content :deep(pre code) {
  background: transparent;
  padding: 0;
  font-size: var(--text-sm);
  color: #d4d4d4;
}

.assistant-content :deep(strong) {
  font-weight: var(--font-semibold);
}

.assistant-content :deep(blockquote) {
  border-left: 2px solid var(--color-accent);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--color-text-secondary);
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/ChatMessage.vue
git commit -m "feat: decard ChatMessage, add Thinking collapse and edit button"
```

---

### Task 9: ToolCall — 重构为展开/折叠

**Files:**
- Modify: `src/components/ToolCall.vue`

- [ ] **Step 1: 重写 ToolCall.vue**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight, ChevronDown, Wrench } from 'lucide-vue-next'

defineProps<{
  tool: string
  args: any
  output?: string
}>()

const expanded = ref(false)

function toggle() {
  expanded.value = !expanded.value
}

function formatJson(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}
</script>

<template>
  <div :class="['tool-call', { expanded }]">
    <!-- Collapsed header -->
    <div class="tool-header" @click="toggle">
      <ChevronRight v-if="!expanded" :size="12" class="chevron" />
      <ChevronDown v-else :size="12" class="chevron" />
      <Wrench :size="14" class="tool-icon" />
      <span class="tool-name">{{ tool }}</span>
      <span v-if="output" class="tool-stat output">done</span>
      <span v-else class="tool-stat pending">...</span>
    </div>

    <!-- Expanded body -->
    <Transition name="expand">
      <div v-if="expanded" class="tool-body">
        <!-- Parameters -->
        <div class="tool-section">
          <div class="tool-section-label">PARAMETERS</div>
          <pre class="tool-code">{{ formatJson(args) }}</pre>
        </div>

        <!-- Result -->
        <div v-if="output" class="tool-section result-section">
          <div class="tool-section-label">RESULT</div>
          <pre class="tool-code">{{ output }}</pre>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tool-call {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  transition: border-color var(--transition-fast);
  animation: message-in var(--transition-normal) var(--ease-out);
}

.tool-call.expanded {
  border-left-color: var(--color-accent);
}

/* Header */
.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.tool-header:hover {
  background: var(--color-surface-hover);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

.tool-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}

.tool-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-accent);
  flex: 1;
}

.tool-stat {
  font-size: var(--text-xs);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.tool-stat.output {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.tool-stat.pending {
  color: var(--color-text-tertiary);
}

/* Body */
.tool-body {
  overflow: hidden;
}

.tool-section {
  padding: 8px 14px;
  border-bottom: 1px solid var(--color-border);
}

.tool-section.result-section {
  background: var(--color-surface-hover);
}

.tool-section-label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.tool-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.6;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/ToolCall.vue
git commit -m "feat: refactor ToolCall as expandable inline with left accent border"
```

---

### Task 10: DiffView 组件（新建）

**Files:**
- Create: `src/components/chat/DiffView.vue`

- [ ] **Step 1: 创建 DiffView.vue**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown, Copy, Undo2 } from 'lucide-vue-next'

interface DiffLine {
  type: 'add' | 'remove' | 'context'
  oldLineNum?: number
  newLineNum?: number
  content: string
}

const props = defineProps<{
  tool: string
  filePath: string
  lines: DiffLine[]
  addedCount?: number
  removedCount?: number
  duration?: string
}>()

const emit = defineEmits<{
  undo: []
}>()

const expanded = ref(false)
const copied = ref(false)
const truncated = computed(() => props.lines.length > 50)
const displayLines = computed(() =>
  truncated.value && !expanded.value ? props.lines.slice(0, 50) : props.lines
)

function toggle() {
  expanded.value = !expanded.value
}

function toggleTruncation() {
  expanded.value = !expanded.value
}

async function handleCopy() {
  const text = props.lines
    .map(l => `${l.type === 'add' ? '+' : l.type === 'remove' ? '-' : ' '} ${l.content}`)
    .join('\n')
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}
</script>

<template>
  <div :class="['diff-view', { expanded }]">
    <!-- Collapsed header -->
    <div class="diff-header" @click="toggle">
      <ChevronRight v-if="!expanded" :size="12" class="chevron" />
      <ChevronDown v-else :size="12" class="chevron" />
      <span class="diff-tool">{{ tool }}</span>
      <span class="diff-path">{{ filePath }}</span>
      <span v-if="addedCount" class="diff-count add">+{{ addedCount }}</span>
      <span v-if="removedCount" class="diff-count remove">−{{ removedCount }}</span>
      <span v-if="duration" class="diff-duration">{{ duration }}</span>
    </div>

    <!-- Expanded body -->
    <Transition name="expand">
      <div v-if="expanded" class="diff-body">
        <!-- Column headers -->
        <div class="diff-columns-header">
          <div class="diff-col old-col">− OLD</div>
          <div class="diff-col new-col">+ NEW</div>
        </div>

        <!-- Side-by-side diff -->
        <div class="diff-content">
          <div v-for="(line, i) in displayLines" :key="i" class="diff-row">
            <!-- Left: OLD -->
            <div :class="['diff-col', 'old-col', line.type === 'remove' ? 'removed' : line.type === 'add' ? 'empty' : '']">
              <span v-if="line.type !== 'add'" class="line-num">{{ line.oldLineNum }}</span>
              <span v-else class="line-num empty-num"></span>
              <span v-if="line.type !== 'add'" class="line-text">{{ line.content }}</span>
              <span v-else class="line-placeholder"></span>
            </div>
            <!-- Right: NEW -->
            <div :class="['diff-col', 'new-col', line.type === 'add' ? 'added' : line.type === 'remove' ? 'empty' : '']">
              <span v-if="line.type !== 'remove'" class="line-num">{{ line.newLineNum }}</span>
              <span v-else class="line-num empty-num"></span>
              <span v-if="line.type !== 'remove'" class="line-text">{{ line.content }}</span>
              <span v-else class="line-placeholder"></span>
            </div>
          </div>
        </div>

        <!-- Truncation hint -->
        <div v-if="truncated" class="diff-truncation" @click="toggleTruncation">
          {{ expanded ? 'Show less' : `Show all ${lines.length} lines` }}
        </div>

        <!-- Actions -->
        <div class="diff-actions">
          <button class="diff-action-btn" @click="handleCopy">
            <Copy v-if="!copied" :size="12" />
            <CheckIcon v-else :size="12" />
            {{ copied ? 'Copied' : 'Copy' }}
          </button>
          <button class="diff-action-btn" @click="emit('undo')">
            <Undo2 :size="12" />
            Undo
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<!-- Inline CheckIcon for copy feedback -->
<script lang="ts">
import { defineComponent, h } from 'vue'
const CheckIcon = defineComponent({
  setup() {
    return () => h('svg', {
      width: 12, height: 12, viewBox: '0 0 24 24',
      fill: 'none', stroke: 'currentColor', 'stroke-width': '2'
    }, [h('polyline', { points: '20 6 9 17 4 12' })])
  }
})
export default { components: { CheckIcon } }
</script>

<style scoped>
.diff-view {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  overflow: hidden;
  animation: message-in var(--transition-normal) var(--ease-out);
}

.diff-view.expanded {
  border-left-color: var(--color-accent);
}

/* Header */
.diff-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.diff-header:hover {
  background: var(--color-surface-hover);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.diff-tool {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-accent);
}

.diff-path {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  flex: 1;
}

.diff-count {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: 1px 4px;
  border-radius: var(--radius-sm);
}

.diff-count.add {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.diff-count.remove {
  color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
}

.diff-duration {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Body */
.diff-body {
  overflow: hidden;
}

.diff-columns-header {
  display: flex;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.diff-col {
  flex: 1;
  padding: 3px 12px;
}

.old-col {
  background: color-mix(in srgb, var(--color-error) 4%, transparent);
}

.new-col {
  background: color-mix(in srgb, var(--color-success) 4%, transparent);
  border-left: 1px solid var(--color-border);
}

/* Rows */
.diff-content {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  line-height: 1.9;
}

.diff-row {
  display: flex;
}

.diff-row .diff-col {
  display: flex;
  align-items: baseline;
}

.diff-col.removed {
  background: color-mix(in srgb, var(--color-error) 8%, transparent);
  color: var(--color-error);
}

.diff-col.added {
  background: color-mix(in srgb, var(--color-success) 8%, transparent);
  color: var(--color-success);
}

.diff-col.empty {
  background: color-mix(in srgb, var(--color-success) 3%, transparent);
}

.diff-col.empty .line-placeholder {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-border), transparent);
  margin: auto 8px;
}

.line-num {
  width: 28px;
  text-align: right;
  flex-shrink: 0;
  margin-right: 8px;
  color: var(--color-text-tertiary);
}

.removed .line-num { color: var(--color-error); }
.added .line-num { color: var(--color-success); }

.empty-num {
  visibility: hidden;
}

.line-text {
  flex: 1;
  white-space: pre;
}

/* Truncation */
.diff-truncation {
  padding: 6px;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-accent);
  cursor: pointer;
  border-top: 1px solid var(--color-border);
}

.diff-truncation:hover {
  text-decoration: underline;
}

/* Actions */
.diff-actions {
  display: flex;
  gap: 4px;
  padding: 6px 12px;
  border-top: 1px solid var(--color-border);
}

.diff-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.diff-action-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/components/chat/DiffView.vue
git commit -m "feat: add side-by-side DiffView component with VS Code-style alignment"
```

---

### Task 11: CodeBlock + ChatInput 重写

**Files:**
- Modify: `src/components/chat/CodeBlock.vue`
- Modify: `src/components/chat/ChatInput.vue`

- [ ] **Step 1: CodeBlock — 深棕顶栏**

替换 `src/components/chat/CodeBlock.vue`：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { Copy, Check } from 'lucide-vue-next'

defineProps<{
  code: string
  language?: string
}>()

const copied = ref(false)

async function handleCopy(code: string) {
  await navigator.clipboard.writeText(code)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}
</script>

<template>
  <div class="code-block">
    <div class="code-header">
      <span class="language">{{ language || 'plaintext' }}</span>
      <button class="copy-btn" @click="handleCopy(code)">
        <Check v-if="copied" :size="12" />
        <Copy v-else :size="12" />
        <span>{{ copied ? 'Copied' : 'Copy' }}</span>
      </button>
    </div>
    <pre><code>{{ code }}</code></pre>
  </div>
</template>

<style scoped>
.code-block {
  background: #1e1e1e;
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 8px 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.code-header {
  padding: 5px 14px;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.language {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
  letter-spacing: 0.5px;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}

.copy-btn:hover {
  color: #ccc;
}

pre {
  padding: 12px 16px;
  margin: 0;
  overflow-x: auto;
}

code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.7;
  color: #d4d4d4;
}
</style>
```

- [ ] **Step 2: ChatInput — 毛玻璃底 + 圆角升级**

替换 `src/components/chat/ChatInput.vue`：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { Send } from 'lucide-vue-next'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [text: string]
}>()

const text = ref('')

function handleSubmit() {
  if (!text.value.trim() || props.loading) return
  emit('submit', text.value)
  text.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <textarea
        v-model="text"
        placeholder="Type a message..."
        @keydown="handleKeydown"
        rows="1"
      ></textarea>
      <div class="input-actions">
        <span class="shortcut-hint">Ctrl ↵</span>
        <button
          class="send-btn"
          :disabled="loading || !text.trim()"
          @click="handleSubmit"
        >
          <Send :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  padding: 12px 16px 16px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 10px 16px;
  box-shadow: var(--shadow-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.input-wrapper:focus-within {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow);
}

.input-wrapper textarea {
  flex: 1;
  min-height: 24px;
  max-height: 120px;
  border: none;
  background: transparent;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  resize: none;
  outline: none;
  line-height: 1.5;
}

.input-wrapper textarea::placeholder {
  color: var(--color-text-tertiary);
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.shortcut-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-primary);
  color: var(--color-bg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast), opacity var(--transition-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/CodeBlock.vue src/components/chat/ChatInput.vue
git commit -m "feat: redesign CodeBlock with accent header and ChatInput with glassmorphism"
```

---

### Task 12: TaskView 集成

**Files:**
- Modify: `src/views/TaskView.vue`

- [ ] **Step 1: 更新 TaskView.vue 集成新组件**

更新 `src/views/TaskView.vue`，引入 DiffView：

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import Sidebar from '../components/layout/Sidebar.vue'
import MainContent from '../components/layout/MainContent.vue'
import ChatPanel from '../components/sidebar/ChatPanel.vue'
import FilesPanel from '../components/sidebar/FilesPanel.vue'
import PluginsPanel from '../components/sidebar/PluginsPanel.vue'
import SettingsPanel from '../components/sidebar/SettingsPanel.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ToolCall from '../components/ToolCall.vue'
import DiffView from '../components/chat/DiffView.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import StatusDot from '../components/ui/StatusDot.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useTask } from '../composables/useTask'
import type { Project } from '../api/client'

// ... (keep existing script logic, same as before) ...

const props = defineProps<{
  project: Project
  activePanel: 'chat' | 'files' | 'plugins' | 'settings'
}>()

const emit = defineEmits<{
  back: []
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings']
}>()

const { tasks, currentTask, loading, submit, loadTasks } = useTask()

const activeTaskId = computed(() => currentTask.value?.id || '')
const { events, connected } = useWebSocket(activeTaskId)

const messages = computed(() => {
  const result: Array<{ type: string; data: any }> = []
  for (const event of events.value) {
    if (event.type === 'message') {
      result.push({ type: 'message', data: event.data })
    } else if (event.type === 'tool_call') {
      result.push({ type: 'tool_call', data: event.data })
    } else if (event.type === 'tool_result') {
      const last = result[result.length - 1]
      if (last?.type === 'tool_call') {
        last.data.output = event.data.output
      }
    } else if (event.type === 'diff') {
      result.push({ type: 'diff', data: event.data })
    }
  }
  return result
})

const taskStatus = computed(() => {
  const statusEvent = [...events.value].reverse().find(e => e.type === 'status')
  return statusEvent?.data.status || currentTask.value?.status || 'pending'
})

const servers = ref([
  { url: 'localhost:8000', status: 'connected' as const },
])

async function handleSubmit(text: string) {
  await submit(props.project.id, text)
}

loadTasks(props.project.id)
</script>

<template>
  <div class="task-view">
    <Sidebar
      v-if="activePanel !== 'settings'"
      :title="activePanel === 'chat' ? 'Chat' : activePanel === 'files' ? 'Files' : 'Plugins'"
    >
      <ChatPanel
        v-if="activePanel === 'chat'"
        :tasks="tasks"
        :active-task-id="activeTaskId"
        @select="currentTask = $event"
      />
      <FilesPanel v-else-if="activePanel === 'files'" />
      <PluginsPanel v-else />
    </Sidebar>

    <SettingsPanel
      v-else
      :servers="servers"
      active-server="localhost:8000"
    />

    <MainContent>
      <div class="chat-header">
        <button class="back-btn" @click="emit('back')">
          <ArrowLeft :size="16" />
        </button>
        <span class="task-title">{{ project.name }}</span>
        <StatusDot :status="taskStatus" />
        <span class="ws-status">{{ connected ? 'connected' : 'disconnected' }}</span>
      </div>

      <div class="messages-area">
        <template v-for="(msg, i) in messages" :key="i">
          <ChatMessage
            v-if="msg.type === 'message'"
            role="assistant"
            :content="msg.data.content"
          />
          <ToolCall
            v-else-if="msg.type === 'tool_call'"
            :tool="msg.data.tool"
            :args="msg.data.args"
            :output="msg.data.output"
          />
          <DiffView
            v-else-if="msg.type === 'diff'"
            :tool="msg.data.tool"
            :file-path="msg.data.filePath"
            :lines="msg.data.lines"
            :added-count="msg.data.addedCount"
            :removed-count="msg.data.removedCount"
          />
        </template>
      </div>

      <ChatInput :loading="loading" @submit="handleSubmit" />
    </MainContent>
  </div>
</template>

<style scoped>
.task-view {
  display: flex;
  flex: 1;
  background: var(--color-bg);
}

.chat-header {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.back-btn {
  padding: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.back-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.task-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.ws-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add src/views/TaskView.vue
git commit -m "feat: integrate DiffView into TaskView message flow"
```

---

### Task 13: App.vue 微调

**Files:**
- Modify: `src/App.vue`

- [ ] **Step 1: 确保 useTheme 正确初始化**

`App.vue` 已经调用了 `useTheme()`，无需大改。确认 `@update:active-panel` 事件正常传递即可。现有代码无需修改。

- [ ] **Step 2: 验证构建**

```bash
cd client && npx vue-tsc --noEmit && npx vite build
```

- [ ] **Step 3: 提交**

```bash
git add src/App.vue
git commit -m "chore: verify App.vue integration with new design system"
```

---

## 自审

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Spec 覆盖 | ✅ | 16 个章节全部有对应任务 |
| 占位符 | ✅ | 所有任务包含完整代码 |
| 类型一致性 | ✅ | props/emit 类型跨组件一致 |
| 文件路径 | ✅ | 所有路径基于实际项目结构 |

## 执行顺序

```
Task 1  (CSS 变量)         ← 基础设施，必须先做
Task 2  (base + 过渡)      ← 依赖 Task 1
Task 3  (UI 原语)          ← 依赖 Task 1
   ↓
Task 4  (首页)             ← 可并行
Task 5  (ActivityBar)      ← 可并行
   ↓
Task 6  (Sidebar + Chat)   ← 可并行
Task 7  (Files/Plugins/Settings) ← 可并行
   ↓
Task 8  (ChatMessage)      ← 核心组件
Task 9  (ToolCall)         ← 核心组件
Task 10 (DiffView)         ← 新组件，可并行
Task 11 (CodeBlock + Input)← 可并行
   ↓
Task 12 (TaskView 集成)    ← 依赖 8-11
Task 13 (App.vue + 构建)   ← 依赖 12
```
