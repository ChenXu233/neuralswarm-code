# NeuralSwarm Kernel API 参考（前端对接用）

> 本文档定义 kernel HTTP/WS 接口，供 client/ 和 desktop/ 对接。
> 对应设计文档：`docs/kernel-core-design.md`

---

## 基础信息

- **Base URL**: `http://localhost:<port>`（默认 8080）
- **响应格式**: `{ "data": ..., "error": ... }`
- **事件推送**: WebSocket

---

## REST API

### 创建会话

```
POST /api/sessions
```

```json
// Request
{ "workspace": { "project": "/path/to/project" } }

// Response
{ "data": { "session_id": "uuid", "workspace": { ... } } }
```

### 发送消息

```
POST /api/sessions/:id/messages
```

```json
// Request
{ "content": "帮我改一下 README.md" }

// Response
{ "data": { "message_id": "uuid", "session_id": "uuid" } }
```

返回后，事件通过 WebSocket 推送。

### 列出会话

```
GET /api/sessions
```

### 获取会话历史

```
GET /api/sessions/:id/messages
```

---

## WebSocket API

### 连接

```
ws://localhost:8080/ws/sessions/:session_id
```

### 推送事件

```json
// 状态变化
{ "type": "status", "data": { "status": "running" } }

// LLM 流式输出
{ "type": "stream", "data": { "content": "正在分析..." } }

// 工具调用
{ "type": "tool_call", "data": {
    "tool": "file_read",
    "args": { "path": "README.md" },
    "status": "running"
}}

// 工具结果
{ "type": "tool_result", "data": {
    "tool": "file_read",
    "args": { "path": "README.md" },
    "output": "..."
}}

// 最终消息（LLM 文本回复）
{ "type": "message", "data": { "content": "改好了，你看一下。" } }

// 错误
{ "type": "error", "data": { "message": "..." } }

// 完成
{ "type": "done", "data": {} }
```

### 前端的职责

| 事件 | 前端表现 |
|------|---------|
| `stream` | 追加到当前 assistant 消息 |
| `tool_call` | 折叠卡片，展开显示参数 |
| `tool_result` | 折叠卡片里显示输出 |
| `message` | 结束当前消息，渲染 markdown |
| `error` | 错误提示 |
| `status` | 状态栏指示器 |

---

## 目录树注入

Kernel 在工作区初始化时注入目录树到 LLM prompt。格式：

```
project/
├── src/
│   ├── main.rs
│   └── lib.rs
├── Cargo.toml
├── README.md
└── docs/
    └── design.md
```

前端不需要关心这个——这是 kernel 内部的事。

---

## 错误处理

```json
// HTTP 错误
{ "error": { "code": "SESSION_NOT_FOUND", "message": "..." } }

// WebSocket 错误
{ "type": "error", "data": { "message": "..." } }
```
