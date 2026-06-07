# NeuralSwarm Client 前端设计规范

> 版本: 2.0 | 日期: 2026-06-07 | 状态: 已确认

---

## 1. 设计原则

四句话定义整个产品的视觉体系。每一个组件决策都回溯到这四个原则。

### 1.1 排版驱动层次，不是卡片

信息的层级关系靠**字号、字重、间距、颜色深浅**来表达。拒绝用卡片把每块内容框起来。
卡片只在真正需要强调或分离的少数场景使用（如工具调用结果展开区、文件预览）。

### 1.2 毛玻璃作为氛围，不作为结构

Glassmorphism 用在背景装饰、侧边栏、悬浮面板——营造**景深感**。
不用在信息容器上。用户不该透过毛玻璃读正文。

### 1.3 呼吸感来自删除，不是添加

与其到处加 padding，不如删掉不必要的元素。一个页面只有必要信息 + 足够留白。
首页只有项目列表和几个操作，不塞功能导览。

### 1.4 统一语言，单一真相源

所有组件共用一个设计 token 体系（CSS 变量）。圆角、阴影、间距、字号都从同一个变量表出。
不要一个组件 8px 圆角、另一个 6px——没有商量余地。

### 一句话总结

> "像一个精心排版的文档编辑器——但它是一个 AI 开发平台。"
> 信息通过排版呼吸，不是通过卡片隔离。深度来自微妙的阴影和毛玻璃，不是粗边框。

---

## 2. 配色系统

### 2.1 Warm Stone（默认）

| Token | 色值 | 用途 |
|-------|------|------|
| `--color-bg` | `#faf8f5` | 页面背景 |
| `--color-surface` | `#ffffff` | 卡片/面板/输入框背景 |
| `--color-surface-hover` | `#f5f3f0` | hover 态 |
| `--color-activity-bg` | `rgba(240, 236, 230, 0.6)` | ActivityBar 背景（毛玻璃） |
| `--color-activity-active` | `rgba(196, 117, 90, 0.08)` | ActivityBar 选中态 |
| `--color-text` | `#2d2a26` | 主文字 |
| `--color-text-secondary` | `#666666` | 次要文字 |
| `--color-text-tertiary` | `#999999` | 辅助文字 |
| `--color-border` | `#e8e4df` | 边框/分割线 |
| `--color-primary` | `#2d2a26` | 主色（深棕） |
| `--color-accent` | `#c4755a` | 强调色（Terracotta 赤陶） |
| `--color-success` | `#52c41a` | 成功/新增 |
| `--color-warning` | `#faad14` | 警告 |
| `--color-error` | `#ff4d4f` | 错误/删除 |

### 2.2 Dark Slate

| Token | 色值 |
|-------|------|
| `--color-bg` | `#1a1d23` |
| `--color-surface` | `#25282e` |
| `--color-surface-hover` | `#2a2d33` |
| `--color-activity-bg` | `rgba(34, 37, 43, 0.6)` |
| `--color-activity-active` | `rgba(107, 140, 255, 0.1)` |
| `--color-text` | `#e0e0e0` |
| `--color-text-secondary` | `#999999` |
| `--color-text-tertiary` | `#666666` |
| `--color-border` | `#2a2d33` |
| `--color-accent` | `#6b8cff`（Slate Blue 岩蓝） |
| `--color-success` | `#4ec9b0` |
| `--color-warning` | `#cca700` |
| `--color-error` | `#f44747` |

### 2.3 Pure Minimal

| Token | 色值 |
|-------|------|
| `--color-bg` | `#ffffff` |
| `--color-surface` | `#fafafa` |
| `--color-surface-hover` | `#f0f0f0` |
| `--color-activity-bg` | `rgba(245, 245, 245, 0.6)` |
| `--color-activity-active` | `rgba(107, 154, 122, 0.08)` |
| `--color-text` | `#111111` |
| `--color-text-secondary` | `#666666` |
| `--color-text-tertiary` | `#999999` |
| `--color-border` | `#eeeeee` |
| `--color-accent` | `#6b9a7a`（Sage Green 鼠尾草绿） |
| `--color-success` | `#52c41a` |
| `--color-warning` | `#faad14` |
| `--color-error` | `#ff4d4f` |

### 2.4 Amber Glow

| Token | 色值 |
|-------|------|
| `--color-bg` | `#0d0d0d` |
| `--color-surface` | `#141414` |
| `--color-surface-hover` | `#1a1a1a` |
| `--color-activity-bg` | `rgba(17, 17, 17, 0.6)` |
| `--color-activity-active` | `rgba(255, 180, 50, 0.1)` |
| `--color-text` | `#ffcc66` |
| `--color-text-secondary` | `#997744` |
| `--color-text-tertiary` | `#554433` |
| `--color-border` | `#222222` |
| `--color-accent` | `#ffb432`（Amber 琥珀金） |
| `--color-success` | `#aacc44` |
| `--color-warning` | `#ffb432` |
| `--color-error` | `#ff6644` |

### 2.5 主题切换

- 通过 `document.documentElement.dataset.theme` 切换（值: `warm-stone` | `dark-slate` | `pure-minimal` | `amber-glow`）
- CSS 变量统一定义在 `:root`，每个主题用 `[data-theme="xxx"]` 覆盖
- 默认主题: `warm-stone`
- 用户选择持久化到 localStorage

---

## 3. 字体与排版

### 3.1 默认字体

| 用途 | 字体栈 |
|------|--------|
| 正文 | `system-ui, -apple-system, 'Segoe UI', sans-serif` |
| 等宽 | `'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace` |

### 3.2 自定义接口

提供 `--font-sans` 和 `--font-mono` CSS 变量，用户可在 Settings 面板自定义字体。

### 3.3 字号刻度

| Token | 字号 | 用途 |
|-------|------|------|
| `--text-xs` | `10px` | 标签、说明、时间戳 |
| `--text-sm` | `12px` | 辅助正文、列表副标题 |
| `--text-base` | `14px` | 正文（基准） |
| `--text-lg` | `16px` | 大正文、强调段落 |
| `--text-xl` | `20px` | 小标题 |
| `--text-2xl` | `26px` | 页面标题 |
| `--text-display` | `36px` | 展示文字（首页品牌） |

### 3.4 字重

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-normal` | `400` | 正文 |
| `--font-medium` | `500` | 标题、强调 |
| `--font-semibold` | `600` | 按钮、导航 |

---

## 4. 圆角与阴影

### 4.1 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | `4px` | 行内代码、小标签 |
| `--radius-md` | `8px` | 按钮、输入框、列表项 |
| `--radius-lg` | `14px` | 气泡、面板、卡片 |
| `--radius-xl` | `20px` | 大型容器 |

### 4.2 阴影

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.06)` | 微妙浮起（气泡） |
| `--shadow-md` | `0 2px 12px rgba(0,0,0,0.05)` | 面板/输入框 |
| `--shadow-lg` | `0 4px 24px rgba(0,0,0,0.08)` | 下拉/弹窗 |
| `--shadow-glow` | `0 0 12px rgba(196,117,90,0.15)` | 聚焦/选中发光 |

---

## 5. 动效系统

### 5.1 CSS 变量

| Token | 值 |
|-------|-----|
| `--transition-fast` | `150ms ease` |
| `--transition-normal` | `200ms ease` |
| `--transition-slow` | `300ms ease` |
| `--ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` |
| `--ease-in-out` | `cubic-bezier(0.65, 0, 0.35, 1)` |

### 5.2 动画清单

| 触发 | 动画 | 时长 |
|------|------|------|
| 页面过渡（首页→选项） | slide-fade | 250ms |
| 页面过渡（选项→任务） | fade + scale(0.98→1) | 200ms |
| 页面过渡（返回首页） | fade | 150ms |
| 新消息入场 | fade + translateY(8px→0) | 200ms |
| 流式文字追加 | 无动画（跟随打字） | — |
| ToolCall/Diff 出现 | 左边框渐显 + translateY(4px→0) | 200ms |
| Thinking 展开/折叠 | max-height + opacity | 200ms |
| ToolCall 展开/折叠 | max-height + opacity | 200ms |
| Chevron 旋转 | rotate(0→90deg) | 150ms |
| 按钮/链接 hover | bg-color / color | 150ms |
| Copy 成功反馈 | 图标 Copy→Check→恢复 | 1500ms |
| StatusDot running | pulse 呼吸 | 2s loop |
| 流式光标闪烁 | opacity 0↔1 | 1s loop |

### 5.3 不用动画的地方

- 流式文字追加（本身就在"动"）
- 列表/文件树渲染（非交互）
- 主题切换（瞬间切换，避免颜色闪烁）
- 滚动（浏览器原生）

---

## 6. 布局结构

### 6.1 整体布局（不变）

```
ActivityBar (48px) | Sidebar (240px) | MainContent (flex:1)
```

三层侧边栏结构：ActivityBar 图标 → 点击展开 Sidebar → 面板内容。

### 6.2 响应式断点

| 断点 | 宽度 | 行为 |
|------|------|------|
| Compact | < 640px | 选项纵向堆叠，ActivityBar 收窄或隐藏，Sidebar 覆盖式展开 |
| Medium | 640–1024px | 选项 2 列，Sidebar 可折叠 |
| Full | ≥ 1024px | 完整三栏布局 |

---

## 7. 首页（HomePage）

### 7.1 视觉参考

VS Code 启动页——简单、干净的左右两栏。

### 7.2 布局

```
┌─────────────────────────────────────────────┐
│                                             │
│         N                                   │
│         NeuralSwarm      │  RECENT          │
│         AI-Powered        │  ~/project-a    │
│         Development       │  ~/project-b    │
│                           │                 │
│                           │  [Open...]      │
│                                             │
└─────────────────────────────────────────────┘
```

- 整体居中漂浮
- 左侧: 品牌区（右对齐）— "N" + NeuralSwarm + 副标题
- 竖线分隔（1px, `--color-border`）
- 右侧: RECENT 标签 + 项目列表 + 时间 + 底部 "Open..." 按钮
- 点击 "Open..." → slide-fade 进入选项页

### 7.3 响应式

- ≥ 768px: 水平排列
- < 768px: 垂直堆叠（品牌在上，列表在下）

---

## 8. 选项页

### 8.1 布局

```
┌─────────────────────────────┐
│      START A SESSION        │
│                             │
│  📂  Open Folder      ⌘O   │
│      Browse a local dir     │
│                             │
│  ✨  New Project       ⌘N   │
│      Start from scratch     │
│                             │
│  🌐  Global Mode       ⌘G   │
│      No project context     │
│                             │
│          ← Back             │
└─────────────────────────────┘
```

- 列表式，每行: 图标 + 标题 + 描述 + 快捷键提示
- Global Mode 用 accent 淡底色强调
- hover 时行背景微亮（`--color-surface-hover`），无边框
- 底部 "← Back" 返回首页
- slide-fade 过渡（保留现有实现）

---

## 9. ActivityBar

### 9.1 设计

- 48px 宽，毛玻璃底（`--color-activity-bg`）+ 右侧 1px 边框
- Logo: 深底反白（`--color-primary` 背景 + 白色文字），30×30px，圆角 8px
- 图标项: 30×30px，圆角 8px，间距 8px
- 选中态: 左侧 2px 竖线（`--color-accent`，圆角右侧）+ accent 淡底色
- 未选中: 灰色图标，hover 时微亮
- 设置图标在底部（margin-top: auto）
- 所有图标使用 lucide-vue-next，14px

---

## 10. Sidebar 面板

### 10.1 ChatPanel

- 头部: "TASKS" 标签（10px, letter-spacing 1.5px）+ 右侧新建按钮（Plus 图标）
- 搜索框: 灰底圆角（`--color-surface-hover`），placeholder "Filter tasks..."
- 任务列表: 每行状态点 + 标题 + 时间
- 选中项: accent 淡底
- 状态点: running 态绿色呼吸动画，idle 灰色静态

### 10.2 FilesPanel

- 头部: "EXPLORER" 标签
- 下方: 工作区文件夹名列表（支持多项目混合），每行文件夹图标 + 名称
- 文件树: 缩进 + Chevron（展开/折叠），不用连接线
- 文件夹图标: Folder（lucide），文件图标: File（lucide）
- 不同文件类型可用不同图标

### 10.3 PluginsPanel

- 列表式，每行插件名 + 启用/禁用开关
- 空状态: 居中提示文字

### 10.4 SettingsPanel

- 列表式分组: 服务器列表、主题选择、字体设置
- 主题: 四个选项，当前选中高亮
- 字体: 输入框，修改 `--font-sans` / `--font-mono`

---

## 11. 消息组件

### 11.1 通用规则

- 全 lucide 图标，零 emoji
- 流式渲染: Thinking 和 Content 各自独立追加，各自独立闪烁光标
- 消息流 = 排版出来，不是卡片拼出来

### 11.2 User 消息

- 右对齐，深色填充背景（`--color-primary`），白色文字
- 圆角: `14px 14px 4px 14px`（左下角小圆角模拟对话方向）
- 字号: `--text-base`（14px）
- 微阴影: `--shadow-sm`
- hover 时左侧出现编辑按钮（Pencil 图标，lucide）
- 点击编辑 → 提示词回到输入框可修改

### 11.3 Assistant 消息

- 左对齐，透明背景，无边框
- 字号: `--text-base`（14px），行高 1.7
- 支持 Markdown 渲染（markdown-it）
- 行内代码: 灰底（`rgba(0,0,0,0.04)`）+ 圆角 3px，字号比正文小 1px

### 11.4 Thinking（思考模式）

- **流式中**: 自动展开，左框线（`--color-border`），文字淡化色（`--color-text-tertiary`），末尾闪烁光标
- **完成后**: 默认折叠
  - 折叠态: 一行 "▶ Thinking · 3s"，ChevronRight 图标
  - 展开态: ChevronDown 图标，内容区左框线 + 淡化文字
- 点击折叠/展开，动画 200ms ease

### 11.5 ToolCall（工具调用）

- **折叠态（默认）**: 左框线（`--color-border`），一行摘要
  - ChevronRight + 工具名（accent 色，加粗）+ 路径/参数摘要 + 右侧统计（+N −M · 72ms）
- **展开态**: 左框线变 accent 色
  - 头部: ChevronDown + 工具名 + 路径 + 统计
  - Parameters 区: 标签（9px）+ JSON（等宽字体，11px）
  - Result 区: 标签（9px）+ 代码内容（等宽字体，11px）
- 展开/折叠动画: 200ms ease
- **无操作按钮**（编辑/重试等不在 ToolCall 内部）

### 11.6 Diff（工具修改差异）

- **折叠态**: 同 ToolCall 折叠态，右侧显示 +N −M 统计
- **展开态**: VS Code 风格左右对照
  - 列头: "− OLD"（左，红淡底）| "+ NEW"（右，绿淡底）
  - 左右行对齐——未变行在两边同高度显示
  - 删除行: 左侧红底红字 + 右侧淡线占位
  - 新增行: 右侧绿底绿字 + 左侧淡线占位
  - 连续插入块: 左侧空白区显示向下箭头（ChevronsDown 图标）提示插入位置
  - 空位行: 淡色渐变横线（`linear-gradient`），表示"这里缺了"
  - 行号: 等宽数字右对齐，变动行跟随颜色（红/绿）
- 超过 50 行默认截断，底部 "View full diff" 链接
- 底部操作栏: Copy（复制 diff 文本）、Undo（撤销修改）
- 小屏（< 640px）切换为上下堆叠
- 字体: `--font-mono`

### 11.7 CodeBlock（代码块）

- 顶栏（`--color-primary` 深棕底）: 左侧语言标签（10px）+ 右侧 Copy 按钮
- 代码区: VS Code 暗底（`#1e1e1e`）+ VS Code 语法高亮色
- Copy 点击 → 图标变 Check → 1.5s 恢复
- 水平溢出时滚动，不换行
- 圆角: `--radius-lg`（10px）包裹整块

---

## 12. 输入框（ChatInput）

- 浮动在 MainContent 底部，左右有 margin（不贴边）
- 毛玻璃底（`rgba(255,255,255,0.7)` + `backdrop-filter: blur(12px)`）
- 圆角: `--radius-lg`（14px）
- 微阴影: `--shadow-md`
- 右侧快捷键提示: `⌘ ↵`（灰底小标签）
- placeholder: "Type a message..."（`--color-text-tertiary`）

---

## 13. 通用 UI 组件

### 13.1 StatusDot

- 8×8px 圆点
- running 态: 绿色 + pulse 呼吸动画（2s loop）
- idle/done 态: 灰色静态
- error 态: 红色静态

### 13.2 Badge（BaseBadge）

- 小圆角标签（`--radius-sm`），字号 10px
- 五种变体: default / primary / success / warning / error
- 通过 CSS 变量自动适配四套主题

### 13.3 IconButton

- 36×36px 方形按钮，圆角 `--radius-md`（8px）
- hover: 背景变 `--color-surface-hover`
- active: accent 淡底色
- 支持 tooltip（title 属性）

---

## 14. CSS 变量完整清单

```css
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
  --color-accent: #c4755a;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.08);
  --shadow-glow: 0 0 12px rgba(196, 117, 90, 0.15); /* 各主题需覆盖此值为对应 accent */
  --font-sans: system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;

  /* 字号 */
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
```

---

## 15. 实施范围

### 15.1 本次范围

| 模块 | 改动类型 |
|------|----------|
| CSS 变量 (`styles/variables.css`) | 重写，引入完整 token 体系 |
| 全局样式 (`styles/base.css`) | 适配新变量，调整字号基准 |
| 过渡动画 (`styles/transitions.css`) | 新增展开/折叠动画 |
| 首页 (`HomePage.vue`) | 重写，VS Code 风格左右两栏 |
| ActivityBar (`ActivityBar.vue`) | 毛玻璃底 + 选中指示线 + lucide 图标 |
| Sidebar 面板 (`ChatPanel/FilesPanel/Plugins/SettingsPanel.vue`) | 精细化，列表式布局 |
| ChatMessage (`ChatMessage.vue`) | 去卡片化，支持 Thinking 折叠 + 流式光标 |
| ToolCall (`ToolCall.vue`) | 重构为展开/折叠，融入消息流 |
| Diff 组件 (**新建**) | 左右对照 diff 视图 |
| ChatInput (`ChatInput.vue`) | 毛玻璃底 + 圆角升级 |
| CodeBlock (`CodeBlock.vue`) | 顶栏改为深棕 + 语言标签 |
| StatusDot / Badge / IconButton | 适配新变量 |

### 15.2 不在此次范围

- 后端 API 对接（FilesPanel 真实数据、Settings 服务器列表等）
- vue-router 引入
- 编辑器功能
- 超级 Agent 交互面板

---

## 16. 不变项（Never Break）

- 现有用户可见交互流程（首页→选项→任务视图）
- WebSocket 连接逻辑
- API 客户端接口
- 组件 props 接口（保持兼容）
- Vue 3 Composition API + `<script setup>` 语法
- Vite 构建配置
