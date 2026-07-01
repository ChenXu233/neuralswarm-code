# NeuralSwarm 前端骨架屏 + UI 插槽系统设计 v1.0

> 版本: 1.0 | 日期: 2026-07-01 | 状态: 草稿

---

## 0. 设计原则

### 0.1 骨架是骨，插件是肉

框架定义一套**固定的 slot 词汇表**，决定"这块区域长什么组件"。插件注册到已有 slot 上，但**不能发明新 slot**。

### 0.2 机制统一，差异只在"声明不声明给别人看"

- 框架层面的 core slot → 骨架组件里留有 `<PluginSlot name="xxx" />` 位置，**公开声明这些位置存在**
- 插件内部的组件组合 → 插件作者自己用 Vue 原生 `<slot>`，**框架不介入、不声明**

两者机制上都是 Vue `<slot>` + `<component :is>`，差异只在于是否被框架声明为公开插槽。

### 0.3 管道钩子用于跨插件数据流

插件间需要"后改前"的地方，走 middleware 链式的管道钩子（hook）。每个钩子接收 ctx，调用 `next()` 传递到下一个。

### 0.4 UI 插件与 kernel 插件一一对应

官方插件的 UI 组件放在 `client/src/plugins/`，与其 kernel handler（`kernel/src/plugins/`）对应。社区插件以**单 dist 分发**（含 core handler + UI bundle + 清单），不拆成两个包。

---

## 1. Core Slot 词汇表（固定，不增不减）

```
┌─────────────────┬──────────────────┬─────────────────────────────────┐
│ activity:action │                  │  main:header                    │
│   [chat][files] │  sidebar:panel   │  ┌─back─┬─Title─┬─header-action┐│
│   [puzzle][mem] │  ┌──────────┐    │  └─────────────────────────────┘│
│                 │  │ 面板组件  │    │                                 │
│                 │  │ (活跃项) │    │  chat:messages                  │
│                 │  │          │    │  ┌──────────────────────────┐   │
│ activity:       │  │          │    │  │ 消息流 + toolcall + diff │   │
│   settings      │  └──────────┘    │  └──────────────────────────┘   │
│   [⚙]          │                  │                                 │
│                 │  sidebar:footer  │  chat:input-toolbar              │
│                 │  ─────────────── │  ┌──────────────────────────┐   │
│                 │                 │  │ [tool1][tool2][tool3]    │   │
│                 │                 │  │                           │   │
│                 │                 │  │  chat:input               │   │
│                 │                 │  │  ┌─────────────────────┐  │   │
│                 │                 │  │  │ Type a message...   │  │   │
│                 │                 │  │  └─────────────────────┘  │   │
│                 │                 │  └──────────────────────────┘   │
│                 │                 │                                 │
└─────────────────┴──────────────────┴─────────────────────────────────┘
                                                                        
  status-bar  ──────────────────────────────────────────────────────────
```

### 1.1 渲染插槽

| Slot | 位置 | 行为 | 当前内置插件 |
|------|------|------|------------|
| `activity:action` | ActivityBar 上半部 | 多个图标按钮，点中切换 sidebar 面板 | Chat, Files, Plugins, Memory |
| `activity:settings` | ActivityBar 底部 | 单个图标按钮 | Settings (⚙) |
| `sidebar:panel` | Sidebar 内容区 | 同一时间只显示一个（活跃 panel） | ChatPanel, FilesPanel, PluginsPanel, MemoryPanel |
| `sidebar:header-action` | Sidebar 标题右侧 | 小图标按钮 | "New Task" (+) 等 |
| `sidebar:footer` | Sidebar 底部 | 固定区域 | 暂无 |
| `main:header` | 主内容区顶部栏 | 单块内容 | 返回按钮 + 标题 + 状态 |
| `main:header-action` | 主内容区 header 右侧 | 多个按钮 | Agents 按钮 |
| `chat:messages` | 消息流 | 按 event type 分派渲染器 | ChatMessage, ToolCall, DiffView, PlanEvent |
| `chat:input` | 输入框 | 大型组件级别 | ChatInput |
| `chat:input-toolbar` | 输入框工具栏 | 多个 icon 按钮 | 暂无 |
| `dialog` | 全局对话框覆盖层 | 单个对话框 | ServerSetupDialog, SettingsPanel |
| `status-bar` | 底部状态栏 | 多个状态指示器 | 连接状态、任务计数 |

> **后续加 slot 的规则**：只有框架作者能加。插件作者有需求走 RFC，框架审核后决定是否纳入固定词汇表。

### 1.2 管道钩子

| Hook | 触发时机 | ctx 内容 | 用途示例 |
|------|---------|---------|---------|
| `message:before-send` | 用户点击发送前 | `{content, files[]}` | 敏感词过滤、自动补全、翻译 |
| `message:before-render` | 消息渲染前 | `{role, content, html}` | markdown 增强、代码高亮、自定义渲染 |
| `tool:before-execute` | toolcall 执行前 | `{tool, args}` | 权限检查、日志记录、参数修改 |
| `tool:after-execute` | toolcall 返回后 | `{tool, args, result}` | 后处理、缓存、统计分析 |

---

## 2. 插件接口

### 2.1 Plugin 类型定义

```ts
// client/src/core/types.ts

// ===== Slot System =====

/** 固定 slot 名称（框架定义，不能发明） */
type SlotName =
  | 'activity:action'
  | 'activity:settings'
  | 'sidebar:panel'
  | 'sidebar:header-action'
  | 'sidebar:footer'
  | 'main:header'
  | 'main:header-action'
  | 'chat:messages'
  | 'chat:input'
  | 'chat:input-toolbar'
  | 'dialog'
  | 'status-bar'

/** 固定 hook 名称（框架定义，不能发明） */
type HookName =
  | 'message:before-send'
  | 'message:before-render'
  | 'tool:before-execute'
  | 'tool:after-execute'

interface SlotRegistration {
  component: Component       // Vue 组件
  order?: 'first' | 'last' | number  // 默认按注册顺序
  /** sidebar:panel 专用：面板的唯一标识 */
  panelId?: string
  /** sidebar:panel 专用：ActivityBar 对应按钮的图标组件 */
  icon?: Component
}

interface HookHandler {
  (ctx: any, next: () => Promise<any>): Promise<any>
}

interface Plugin {
  id: string
  name: string
  description?: string

  slots?: Partial<Record<SlotName, SlotRegistration>>
  hooks?: Partial<Record<HookName, HookHandler>>
}
```

### 2.2 注册函数

```ts
// client/src/core/plugin-registry.ts

function registerPlugin(plugin: Plugin): void
function unregisterPlugin(pluginId: string): void
function getSlotRegistrations(slot: SlotName): SlotRegistration[]
function runHook(hook: HookName, ctx: any): Promise<any>
```

### 2.3 PluginSlot 组件

```vue
<!-- client/src/core/plugin-slot.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { getSlotRegistrations } from './plugin-registry'

const props = defineProps<{ name: SlotName }>()
const registrations = computed(() => getSlotRegistrations(props.name))
</script>

<template>
  <template v-for="reg in registrations" :key="reg.panelId || reg.component">
    <component :is="reg.component" v-bind="$attrs" />
  </template>
</template>
```

对于特殊行为（如 `sidebar:panel` 需要活跃切换），骨架组件直接使用 `getSlotRegistrations` + 自行管理状态，而非使用 PluginSlot 通用组件。

---

## 3. 目录结构

### 3.1 官方内置插件

```
client/src/
  core/                      ← 新增：骨架核心
    plugin-registry.ts       ← 注册中心（单例）
    plugin-slot.vue          ← 通用 slot 渲染组件
    types.ts                 ← SlotName, Plugin 等类型
    pipeline.ts              ← 管道引擎（hook 执行链）
    dynamic-loader.ts        ← 社区插件动态加载器（预留）

  plugins/                   ← 新增：UI 插件，与 kernel 插件一一对应
    chat-panel/              ← 聊天面板（对应 kernel: 聊天面板）
      index.ts               ← 调用 registerPlugin() 注册
      ChatPanel.vue          ← 从 components/sidebar/ 迁入
      ChatAction.vue         ← ActivityBar 图标
    file-tree/               ← 文件树（对应 kernel: file_ops）
      index.ts
      FilesPanel.vue         ← 从 components/sidebar/ 迁入
    memory-panel/            ← 记忆（对应 kernel: memory）
      index.ts
      MemoryPanel.vue
      MemoryAction.vue
    settings/                ← 设置
      index.ts
      SettingsPanel.vue
      SettingsAction.vue
    conflict-dialog/         ← 冲突弹窗（对应 kernel: 并发控制）
      index.ts
      ConflictDialog.vue
    status-bar/              ← 状态栏
      index.ts
      StatusBarPanel.vue

  components/                ← 保留：通用 UI 组件（跨插件共享）
    ui/
      StatusDot.vue
      IconButton.vue
      BaseBadge.vue
      PlatformBanner.vue
    chat/
      ChatMessage.vue
      ChatInput.vue
      CodeBlock.vue
      DiffView.vue
    layout/
      ActivityBar.vue
      Sidebar.vue
      MainContent.vue
    ToolCall.vue
    McpToolCall.vue
    EventStream.vue
    TaskQueue.vue
    AgentPanel.vue
    HomePage.vue
    ServerSetupDialog.vue

  views/
    TaskView.vue             ← 保留（调用骨架 slot 而非 direct import）

  styles/
    variables.css            ← 保留（唯一设计 token 源）
    base.css                 ← 保留
    transitions.css          ← 保留

  App.vue                    ← 重构为骨架 shell
  main.ts                    ← 保留 + 插件初始化
```

### 3.2 社区插件（未来，预留设计）

```
my-plugin/
  dist/
    manifest.json            ← 插件清单：名称、注册的 slot/hook、连接信息
    plugin.umd.js            ← Vue 组件 bundle（defineComponent + registerPlugin）
    handler                  ← gRPC server binary / MCP server
  src/
    ui/                      ← Vue 组件源码
    handler/                 ← handler 源码
```

`manifest.json` 示例：
```json
{
  "id": "community:super-formatter",
  "name": "Super Formatter",
  "version": "1.0.0",
  "slots": {
    "chat:input-toolbar": {
      "order": "last"
    }
  },
  "hooks": {
    "message:before-render": {}
  },
  "transport": {
    "type": "grpc",
    "endpoint": "127.0.0.1:9123"
  }
}
```

前端 `dynamic-loader.ts` 在启动时扫描已注册的社区插件，fetch `plugin.umd.js` 并执行注册。

> **当前不实现动态加载器**。此设计仅预留接口形态，确保 slot 系统兼容未来动态加载。

---

## 4. 迁移方案（不破坏现有功能）

### 4.1 核心迁移思路

目前 `App.vue` 直接 import 所有组件并通过 `v-if` 切换：
```
App.vue
  ├─ ActivityBar         → 硬编码图标+点击事件
  ├─ Sidebar             → 硬编码 v-if 切换 panel
  │   ├─ ChatPanel
  │   ├─ FilesPanel
  │   ├─ PluginsPanel
  │   └─ MemoryPanel
  ├─ HomePage / TaskView → v-if='selectedProject'
  └─ SettingsPanel       → v-if='showSettings'
```

第一阶段：**App.vue 的 import 拆到 plugin index.ts**
```
App.vue（精简）
  ├─ ActivityBar         → 从 registry 读 activity:action
  ├─ Sidebar             → 从 registry 读 sidebar:panel
  │   ├─ <PluginSlot name="sidebar:panel" />
  │   （面板切换由 Sidebar 管理 activePanelId）
  ├─ HomePage / TaskView → v-if 不变
  └─ <PluginSlot name="dialog" />
```

第二阶段：**保持 export 兼容**，确保其他导入路径不报错：
```ts
// plugins/chat-panel/index.ts
export { default as ChatPanel } from './ChatPanel.vue'
// 同时 registerPlugin({...})
```

这样如果任何文件仍然 `import { ChatPanel } from '@/components/sidebar/ChatPanel.vue'`，迁移过程中也能正常工作。

### 4.2 分步执行

| 步骤 | 内容 | 风险 |
|------|------|------|
| 1. 新增 `core/` 骨架 | 注册中心、types、PluginSlot 组件 | 无风险（纯新增） |
| 2. 新增 `plugins/` 目录 | 每个插件建目录 + index.ts 注册 | 无风险（纯新增） |
| 3. 迁移组件到 plugins/ | 复制组件文件，保留原位置 export 兼容 | 低（export 别名） |
| 4. 重构 App.vue | ActivityBar/Sidebar 改为从 registry 读 | 中（需验证面板切换） |
| 5. 骨架测试通过 | 所有现有功能正常 | — |
| 6. 删除旧组件文件 | 清理 sources | 确认步骤 5 完全通过后 |

### 4.3 保证不退化的检查清单

- [ ] ActivityBar 图标点击切换面板
- [ ] 侧边栏面板切换（Chat↔Files↔Plugins↔Memory）
- [ ] 首页→选项→任务视图的流程
- [ ] 消息发送/接收/流式渲染
- [ ] ToolCall 折叠/展开
- [ ] DiffView 渲染
- [ ] 主题切换（4 套）
- [ ] 设置面板打开/关闭
- [ ] 服务器设置弹窗
- [ ] 插件加载不影响其他插件注册
- [ ] 无额外的构建步骤变化

---

## 5. 与 shadcn-vue + Tailwind 的集成策略

### 5.1 Tailwind 配置原则

- CSS 变量保持为**唯一真相源**，Tailwind 只作为消费端
- `tailwind.config.ts` 的 `colors`、`fontSize`、`borderRadius` 等全部引用 `var(--)` 变量
- **禁用 `@tailwind base`**，避免 preflight 与 `base.css` 的 reset 冲突
- 禁用 Tailwind 的 dark mode（`darkMode` 不启用），主题切换完全由 `data-theme` + CSS 变量控制

### 5.2 迁移策略

| 时机 | 内容 |
|------|------|
| 骨架层 | 保持现有 CSS 变量体系，**不引入 Tailwind** |
| 现有组件 | **不改动**，继续使用 `<style scoped>` + `var(--)` |
| 新增 shadcn 组件 | 生成后手动将 Tailwind class 替换为引用 CSS 变量的版本 |

### 5.3 tailwind.config.ts 模板

```ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  // 不启用 darkMode——主题完全由 data-theme + CSS 变量控制
  theme: {
    extend: {
      colors: {
        // 所有颜色引用 CSS 变量，主题切换自动适配
        bg: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        'surface-hover': 'var(--color-surface-hover)',
        text: 'var(--color-text)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-tertiary': 'var(--color-text-tertiary)',
        border: 'var(--color-border)',
        'border-strong': 'var(--color-border-strong)',
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        accent: 'var(--color-accent)',
        'accent-hover': 'var(--color-accent-hover)',
        'accent-soft': 'var(--color-accent-soft)',
        success: 'var(--color-success)',
        'success-soft': 'var(--color-success-soft)',
        warning: 'var(--color-warning)',
        'warning-soft': 'var(--color-warning-soft)',
        error: 'var(--color-error)',
        'error-soft': 'var(--color-error-soft)',
        info: 'var(--color-info)',
        'info-soft': 'var(--color-info-soft)',

        // activity bar
        'activity-bg': 'var(--color-activity-bg)',
        'activity-active': 'var(--color-activity-active)',

        // sidebar
        'sidebar-bg': 'var(--color-sidebar-bg)',
        'sidebar-border': 'var(--color-sidebar-border)',

        // glass
        'glass-bg': 'var(--color-glass-bg)',
        'glass-border': 'var(--color-glass-border)',

        // overlay
        overlay: 'var(--color-overlay)',
        'overlay-light': 'var(--color-overlay-light)',

        // shadcn-vue 兼容别名
        background: 'var(--color-bg)',
        foreground: 'var(--color-text)',
        muted: 'var(--color-surface-hover)',
        'muted-foreground': 'var(--color-text-secondary)',
        card: 'var(--color-surface)',
        'card-foreground': 'var(--color-text)',
        popover: 'var(--color-surface)',
        'popover-foreground': 'var(--color-text)',
        destructive: 'var(--color-error)',
        'destructive-foreground': '#ffffff',
        ring: 'var(--color-focus-ring)',
        input: 'var(--color-surface)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
      fontSize: {
        xs: 'var(--text-xs)',
        sm: 'var(--text-sm)',
        base: 'var(--text-base)',
        lg: 'var(--text-lg)',
        xl: 'var(--text-xl)',
        '2xl': 'var(--text-2xl)',
        '3xl': 'var(--text-3xl)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
        display: 'var(--font-display)',
      },
      spacing: {
        'activity-bar': 'var(--activity-bar-width)',
        sidebar: 'var(--sidebar-width)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],  // shadcn 动画依赖
}
```

---

## 6. 不变项（Never Break）

- 现有用户可见交互流程（首页→选项→任务视图）
- WebSocket 连接逻辑
- API 客户端接口
- Vue 3 Composition API + `<script setup>` 语法
- Vite 构建配置
- 组件 props 接口（保持兼容）
- 主题切换（4 套，通过 CSS 变量 + data-theme）

---

## 7. 待办/未决事项

- [ ] 动态加载器的具体实现（社区插件，后期）
- [ ] shadcn-vue 组件替换的优先级（哪些组件优先迁移）
- [ ] 与 `vue-router` 的整合时机（目前声明了依赖但未使用）
- [ ] 骨架 shell 的响应式断点是否需要调整
