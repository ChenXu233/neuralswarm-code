# NeuralSwarm/Code Kernel 核心设计 v0.1

> 本文档定义 kernel/ 的架构设计与模块边界。
> 验收标准见《验收标准/MVP-核心骨架与单节点闭环.md》，完整架构愿景见《白皮书》。

---

## 1. 设计边界

### 1.1 这份文档覆盖什么

只覆盖 **`kernel/`**——Rust 节点二进制。其他组件各自独立：

| 组件 | 技术栈 | 状态 |
|------|--------|------|
| **kernel/** | Rust（tokio + axum） | **从零设计，本文档** |
| client/ | Vue 3 + TypeScript | 独立开发，调 kernel API |
| desktop/ | Tauri v2 | WebView 壳，连 kernel |
| mobile/ | Capacitor（以后） | 空目录 |
| server/ | Python FastAPI | **废弃** |

### 1.2 MVP 范围

| 做 | 不做 |
|---|------|
| 点注册表 + 管道引擎 + Handler trait | libp2p / Gossip |
| 朴素 LLM 调用（cliark/litellm） | 融合 LLM（多 provider/fallback） |
| file_read / file_write / shell | 记忆插件 |
| 工作区映射（单节点路径解析） | Spec 插件 |
| axum HTTP/WS API | 并发控制 |
| SQLite 本地存储 | 能力令牌 |
| | 多节点路由 |

---

## 2. 目录结构

```
kernel/
├── Cargo.toml
└── src/
    ├── main.rs              # 启动：注册插件 → 启动 server
    │
    ├── kernel/              # 内核实现（零或极少外部依赖）
    │   ├── mod.rs           # pub re-exports
    │   ├── handler.rs       # pub trait Handler （~30行）
    │   ├── context.rs       # pub struct Context （~50行）
    │   ├── registry.rs      # 点注册表 + 拓扑序 （~150行）
    │   ├── pipeline.rs      # 管道引擎 （~100行）
    │   └── workspace.rs     # 工作区路径映射 （~80行）
    │
    ├── plugins/             # 官方插件，各占独立目录
    │   ├── mod.rs           # 收集所有插件注册函数
    │   ├── llm/             # 朴素 LLM 调用
    │   │   ├── mod.rs       # pub fn register(registry)
    │   │   └── handler.rs   # 包装 clark-agent 循环
    │   ├── file_ops/        # file_read / file_write
    │   │   ├── mod.rs
    │   │   └── handler.rs
    │   └── shell/           # shell 命令
    │       ├── mod.rs
    │       └── handler.rs
    │
    └── server/              # HTTP/WS 服务（axum）
        ├── mod.rs
        ├── http.rs          # REST API
        └── ws.rs            # WebSocket（流式事件推送）
```

---

## 3. 内核三件套

### 3.1 Handler trait（扩展契约）

```rust
use async_trait::async_trait;

#[async_trait]
pub trait Handler: Send + Sync {
    async fn invoke(&self, ctx: Context) -> Result<Context>;
}
```

插件只需要实现这个 trait，挂到点上，管道就会调。**插件不需要知道管道细节。**

### 3.2 Context（流经管道的唯一数据载体）

```rust
pub struct Context {
    pub session_id: String,
    pub trace_id: String,
    pub messages: Vec<Message>,
    pub tool_calls: Vec<ToolCall>,
    pub tool_results: Vec<ToolResult>,
    pub terminated: bool,
    pub extras: HashMap<String, Value>,
}
```

`extras` 是兜底——插件间按 key 约定传递非核心字段（如 LLM thinking、工具中间状态）。

`Message` / `ToolCall` / `ToolResult` 是朴素的 Rust struct，不绑定任何 provider 格式。litellm-rs 或 clark-agent 在插件内部做格式转换。

### 3.3 点注册表

```rust
pub struct HandlerRegistration {
    pub id: String,
    pub handler: Arc<dyn Handler>,
    pub before: Vec<String>,
    pub after: Vec<String>,
}

pub struct Registry {
    points: HashMap<&'static str, Point>,
}
```

**固定词汇表**（MVP）：

| 点 | 谁挂 | 流经数据 |
|----|------|---------|
| `user-message` | — | 用户原始输入 |
| `llm-prompt` | 记忆/Spec 插件 | 注入上下文片段 |
| `llm-response` | LLM 插件 | LLM 返回 |
| `tool-execute.before` | 并发控制插件 | 拦截/放行 |
| `tool-execute.after` | 审计插件 | 记录执行结果 |
| `tool-result` | — | 工具结果回灌 |
| `tool:<name>` | 工具插件 | 工具调用参数 → 结果 |
| `lifecycle:start` | 各插件 | 初始化时机 |

- 插件「不能发明新点」——注册到词汇表外的点 → Registry 报错
- before/after 依赖在 register 时校验，拓扑序排序后缓存
- 循环依赖 → register 报错

### 3.4 管道引擎

```rust
pub async fn invoke(&self, point: &str, mut ctx: Context) -> Result<Context> {
    let handlers = self.registry.get_handlers(point)?;
    for handler in &handlers {
        if ctx.terminated { break; }
        ctx = handler.invoke(ctx).await?;
    }
    Ok(ctx)
}
```

管道不知道 agent 循环、不知道 LLM。它只是按序调 handler。

---

## 4. 工作区

```rust
pub enum Location {
    Local(PathBuf),         // MVP：本机路径
    // Remote(NodeId, PathBuf),  // 未来：远程节点
}

pub struct Workspace {
    mounts: HashMap<String, Location>,
}

impl Workspace {
    pub fn mount(&mut self, name: &str, path: PathBuf);
    pub fn resolve(&self, relative: &str) -> Result<PathBuf>;
    pub fn tree(&self) -> String;  // 生成目录树注入 prompt
}
```

MVP 下 Owner ≡ 本机，但数据结构以 `Location` 枚举预留了未来多节点形态。

---

## 5. 启动流程（main.rs）

```rust
#[tokio::main]
async fn main() -> Result<()> {
    // 1. 初始化工作区（从配置加载挂载）
    let mut ws = Workspace::new();
    ws.mount("project", std::env::args().nth(1).unwrap_or("."));

    // 2. 初始化注册表
    let mut registry = Registry::new();

    // 3. 注册内置插件
    plugins::register_all(&mut registry);

    // 4. 创建管道
    let pipeline = Arc::new(Pipeline::new(registry));

    // 5. 启动 HTTP/WS 服务
    Server::new(pipeline, ws).serve(8080).await
}
```

---

## 6. 插件架构

### 6.1 插件注册契约

```rust
// plugins/mod.rs
pub fn register_all(registry: &mut Registry) {
    llm::register(registry);
    file_ops::register(registry);
    shell::register(registry);
}
```

每个插件 `register()` 函数内部调用 `registry.register(point, reg)`，挂自己的 handler。

### 6.2 LLM 插件

| 依赖 | 用途 |
|------|------|
| clark-agent | Agent 循环骨架 |
| litellm-rs | HTTP LLM 调用（多 provider 抽象） |

**内部结构：**

```
plugins/llm/
├── mod.rs          // 注册 llm-prompt → llm-response
├── handler.rs      // 实现 Handler，内部包装 clark-agent 循环
└── tool_bridge.rs  // clark-agent ToolRegistry → pipeline::invoke
```

**工作流程：**

```
clark-agent 循环:
  1. 收到 ctx（已有 messages + tool_results）
  2. 调 litellm-rs → HTTP POST 到 LLM
  3. LLM 返回：
     a. 文本 → 写入 messages，返回 ctx
     b. toolcall → 经过 tool_bridge → pipeline::invoke("tool:<name>", ctx)
        → 拿到结果 → 回灌 clark-agent 继续循环
```

### 6.3 文件操作插件

```rust
// 挂到 tool:file_read / tool:file_write
impl Handler for FileReadHandler {
    async fn invoke(&self, mut ctx: Context) -> Result<Context> {
        // 从 tool_calls 解析出 path
        // workspace.resolve(path) -> 绝对路径
        // 读取文件
        // 结果写入 tool_results
        Ok(ctx)
    }
}
```

`file_ops` 和 `shell` 是纯 handler，不依赖 clark-agent 或任何框架。

---

## 7. 错误处理策略

| 场景 | 行为 |
|------|------|
| handler.invoke 返回 Err | 管道中断，Err 冒泡给调用方 |
| 点不存在 | registry.get_handlers 返回 Err |
| toolcall 工具不存在 | `tool_results` 写入错误消息，管道继续 |
| LLM 调用超时 | clark-agent 循环里重试（由 clark-agent 策略决定） |

---

## 8. 测试策略

| 层级 | 测试内容 |
|------|---------|
| 单元 | Registry 拓扑序排序、循环依赖检测、未知点拒绝 |
| 单元 | Pipeline 按序调用、terminated 截停 |
| 集成 | 注册 handler → pipeline invoke → 验证 ctx 字段变化 |
| 端到端 | 启动 kernel → HTTP POST 消息 → 验证 WebSocket 收到事件 |

---

## 9. modules.txt（前端 AI 对接参考）

> 见独立文件 `docs/kernel-api-reference.md`——定义前端通过 HTTP/WS 看到的 kernel 接口。
