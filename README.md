# NeuralSwarm/Code

> **去中心化云 AI IDE** · **Decentralized Cloud AI IDE**
>
> 在任何设备上用自然语言指挥 AI，操作任何机器上的项目——无需同步代码、无需配置环境。
>
> Command AI from any device to work on projects across any machine — no code sync, no environment setup.

---

## 项目宣言 / Manifesto

**NeuralSwarm/Code 不替代 Claude Code、Cursor、Copilot。** 它是一个**去中心化的神经元网络**——每台机器是一个平权节点，一个信任域对外是一台逻辑计算机：统一寻址、统一调用，物理分布对使用者透明。

**NeuralSwarm/Code is not a Claude Code / Cursor / Copilot replacement.** It is a **decentralized neural network** — every machine is an equal node, and a trust domain presents itself as a single logical computer: unified addressing, unified invocation, with physical distribution transparent to the user.

| 机制 / Mechanism | 说明 / Description |
|-----------------|-------------------|
| **统一插件原语** | 一切扩展都是"一个 handler 绑定到一个具名的点"。工具、拦截器、上下文源、UI 组件——同一个原语 |
| **资源寻址路由** | 不靠插件自报标签，靠调用碰到的资源地址推导执行位置 |
| **工作区** | 模型眼里是一个统一的文件树，内核翻译成"哪个项目、哪个节点" |
| **域 = 一台计算机** | 统一寻址、统一调用，物理分布对插件作者透明 |
| **能力令牌** | 权限跟项目走，不以账户为中心。跨域协作持令牌进入 |

**解决的问题 / Problems Solved:**

- ❌ 工具绑定本地 → ✅ **网络中任意节点可达**
- ❌ 多设备上下文断裂 → ✅ **域内共享上下文，换设备 = 换屏幕**
- ❌ 跨机协作靠 Git 推送 → ✅ **持令牌进域，原地执行，不需 push/pull**

> 详细理念见 [白皮书 v2.0](docs/白皮书.md)

---

## 🧱 系统架构 / Architecture

```
┌─ 信任域（一台逻辑计算机）─────────────────────────────────┐
│                                                           │
│  ┌─ 节点 ───────────────────────────────────┐            │
│  │                                            │            │
│  │  UI 壳 (Tauri / Web)                      │            │
│  │    └─ Vue 3 骨架屏 + 插槽系统              │            │
│  │       └─ UI 插件 (注册到固定插槽)          │            │
│  │                                            │            │
│  │  内核 (Rust) — 六个机制                    │            │
│  │    ├─ 点注册表        ─ 固定扩展点          │            │
│  │    ├─ 管道引擎        ─ agent 控制流骨架   │            │
│  │    ├─ 传输适配        ─ native/gRPC/MCP    │            │
│  │    ├─ 寻址路由        ─ 资源地址 → 节点     │            │
│  │    ├─ 域成员 & Gossip ─ P2P 发现/同步      │            │
│  │    └─ 令牌闸门        ─ 调用授权校验        │            │
│  │                                            │            │
│  │  官方插件 (native)                         │            │
│  │    ├─ 朴素 LLM       ─ 模型端点调用         │            │
│  │    ├─ 基础工具        ─ file_read/write/shell│           │
│  │    ├─ 记忆 / Spec / 并发控制               │            │
│  │    └─ UI 官方组件     ─ 聊天/文件树/设置     │            │
│  │                                            │            │
│  │  SQLite (本地状态 + 域级状态副本)           │            │
│  └────────────────────────────────────────────┘            │
│                                                           │
│         ↕ gRPC                 ↕ MCP (stdio/SSE)          │
│   社区插件 (任意语言)     外部 MCP 工具生态                │
│         ↕ libp2p (GossipSub / Kademlia / mDNS)            │
│   信任域内其他节点                                        │
└───────────────────────────────────────────────────────────┘
```

**内核只有六个机制，零 AI 逻辑、零具体工具、零 LLM 实现**——所有能力都是绑在点上的 handler，包括 LLM 调用本身。

> 详细技术选型见 [技术架构选型](docs/技术架构选型.md)
> 插件体系见 [官方插件设计](docs/官方插件设计.md)

---

## 📦 项目结构 / Project Structure

```
neuralswarm-code/
├── kernel/                 # Rust 内核 — 六机制实现
│   └── src/
│       ├── kernel/         #   点注册表 · 管道引擎 · 寻址路由 · 工作区
│       ├── plugins/        #   官方插件 (llm / file_ops / shell)
│       ├── server/         #   HTTP/WS 服务 (axum)
│       └── main.rs         #   单二进制入口
│
├── client/                 # Vue 3 前端 — 骨架屏 + 插槽系统
│   └── src/
│       ├── core/           #   注册中心 / PluginSlot / 管道引擎
│       ├── plugins/        #   UI 插件 (chat / file-tree / memory / ...)
│       ├── components/     #   通用 UI 组件 (StatusDot / IconButton / ...)
│       ├── views/          #   页面视图 (HomePage / TaskView)
│       ├── composables/    #   Vue 组合式逻辑
│       └── styles/         #   设计 token / 主题 / Tailwind
│
├── desktop/                # Tauri v2 桌面壳 (可选)
│
├── core/ (legacy)          # Rust 客户端核心 (演进中 → kernel/)
│
├── server/ (legacy)        # Python/FastAPI (v1.0 架构，迁移中)
│
└── docs/                   # 文档
```

> **状态说明**：`kernel/` 是新的 Rust 单体二进制（v2.0 架构），正在迭代中。`server/` (Python/FastAPI) 和 `core/` (Rust) 是 v1.0 的遗留代码，功能正逐步迁移到 `kernel/`。

---

## 🚦 当前阶段 / Current Status

**正在构建 MVP：核心骨架 + 单节点闭环**。当前可运行的部分：

| 模块 | 状态 | 说明 |
|------|------|------|
| Rust 内核 (六机制) | 🚧 开发中 | 点注册表、管道引擎、寻址路由基础实现 |
| 基础插件 (LLM/file_ops/shell) | 🚧 开发中 | native transport，单节点运行 |
| 前端骨架屏 + 插槽系统 | ✅ 已完成 | Vue 3 + TypeScript，注册中心 / PluginSlot |
| 前端测试 (22 tests, 92% 覆盖率) | ✅ 已完成 | Vitest + Playwright + CI 工作流 |
| UI 组件 (7 个官方插件) | ✅ 已完成 | Chat / FileTree / Memory / Settings / ... |
| 设计系统 (4 主题 + Tailwind) | ✅ 已完成 | CSS 变量体系 + Tailwind utility 层 |
| v1.0 Python 服务端 | ⏳ 废弃中 | 功能迁移到 Rust 内核后移除 |
| P2P 网络 (libp2p) | ⏳ 待开始 | 节点发现 + Gossip + 资源寻址路由 |
| 安全 (能力令牌) | ⏳ 待开始 | 令牌签发/校验/跨域协作 |
| 融合 LLM (多 provider) | ⏳ 待开始 | 升级版，后期实现 |

---

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- **Rust** 1.80+ (内核)
- **Node.js** 18+ (前端)
- **pnpm** 或 **npm** (前端构建)

### 运行前端 / Run Frontend

```bash
cd client
npm install
npm run dev        # 开发服务器 → http://localhost:5173
npm test           # 运行 22 个测试
npm run test:e2e   # Playwright E2E
```

### 运行内核 (开发中) / Run Kernel (WIP)

```bash
cd kernel
cargo build
cargo run          # 启动 HTTP/WS 服务
```

### Docker 部署 / Docker Deployment

NeuralSwarm 节点分两种角色：

**用户神经元（含 Web UI）：**
```bash
docker compose up -d user-neuron
# 浏览器打开 http://localhost:8000
```

**计算神经元（仅内核，无 UI）：**
```bash
docker compose up -d compute-neuron
# API 端口 http://localhost:8001
```

**开发模式（前端热重载）：**
```bash
docker compose --profile dev up -d kernel-dev
cd client && npm run dev
```

> 详见 [docker/README.md](docker/README.md)

---

## 🧪 测试 / Testing

| 层次 | 工具 | 覆盖 |
|------|------|------|
| 单元测试 | Vitest | 注册中心 / 管道引擎 / PluginSlot |
| 组件测试 | vue-test-utils | ActivityBar / Sidebar |
| E2E | Playwright | App 加载 / 面板切换 / 主题切换 |
| CI | GitHub Actions | TypeScript + 测试 + E2E + 构建 |

当前 **22 个测试，91.86% 覆盖率**，CI 自动运行。

---

## 📖 文档 / Documentation

| 文档 | 内容 |
|------|------|
| [白皮书 v2.0](docs/白皮书.md) | 产品宣言 + 完整技术架构 |
| [技术架构选型](docs/技术架构选型.md) | 技术栈决策与选型理由 |
| [官方插件设计](docs/官方插件设计.md) | 13 个官方插件的设计 |
| [前端设计规范](docs/前端设计/design-spec.md) | 4 套主题 / 设计 token / 组件规范 |
| [前端 Slot 设计](docs/前端设计/slot-design.md) | 骨架屏 + 固定插槽系统设计 |

---

## 🤝 贡献 / Contributing

**内核 + 官方插件以 Apache 2.0 协议开源。** 社区可自由提交插件到插件市场。

- 功能请求 / Bug 报告 → [Issues](https://github.com/ChenXu233/neuralswarm-code/issues)
- Pull Requests → 请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证 / License

Apache 2.0 — 详见 [LICENSE](LICENSE)

## 🙏 致谢 / Acknowledgments

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) — transport 三档之一
- [Tauri](https://tauri.app/) — 跨平台桌面壳
- [libp2p](https://libp2p.io/) — 去中心化 P2P 网络层
- [Vue 3](https://vuejs.org/) + [Tailwind CSS](https://tailwindcss.com/) — 前端框架与工具链
