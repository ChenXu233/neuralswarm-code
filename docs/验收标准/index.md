# NeuralSwarm/Code 验收标准

> 每个里程碑是三条轨道的集成点，而非串行阶段。
>
> 参考文档：
> - [白皮书](../白皮书.md) — 系统设计和功能定义
> - [技术架构选型](../技术架构选型.md) — 技术栈和开发路径
> - [总体设计](../superpowers/specs/2026-06-06-overall-design.md) — 里程碑和阶段划分
> - [架构重设计](../superpowers/specs/2026-06-08-neuralswarm-architecture-redesign.md) — 新架构设计

## 目录结构约定

```
neuralswarm-code/
├── server/          # Python/FastAPI 服务器（Track A）
├── client/          # Vue 前端（三端共用：桌面、Web、移动端）（Track C）
├── core/            # Rust Client Core（桌面、移动端复用）（Track B）
├── desktop/         # Tauri 壳（复用 client/ + core/）（Track C）
├── mobile/          # 移动端原生壳（复用 client/ + core/）（M7）
├── docker/          # Docker Compose 部署配置
└── docs/            # 文档
```

## 三轨并行架构

```mermaid
gantt
    title NeuralSwarm 里程碑路线图
    dateFormat  YYYY-MM
    axisFormat  %Y-%m

    section Track A 服务器
    M1 服务器核心           :done, m1a, 2026-06, 2026-06
    M2 MVP                  :done, m2a, 2026-06, 2026-07
    M3 资源访问             :done, m3a, 2026-07, 2026-08
    M4 多Agent + Worktree    :done, m4a, 2026-08, 2026-09
    M5 MCP协议 + 认知层     :m5a, 2026-09, 2026-11
    M6 调度 + 安全          :m6a, 2026-11, 2027-01
    M7 高级功能 + 移动端    :m7a, 2027-01, 2027-03
    M8 优化 + 稳定性        :m8a, 2027-03, 2027-05

    section Track B Client Core
    M5 MCP Server实现       :m5b, 2026-09, 2026-11

    section Track C UI
    M2 Tauri基础UI          :done, m2c, 2026-06, 2026-07
    M3 资源访问可视化       :done, m3c, 2026-07, 2026-08
    M4 冲突通知 + 多Agent视图 :done, m4c, 2026-08, 2026-09
    M5 MCP工具 + 记忆UI     :m5c, 2026-09, 2026-11
    M6 调度决策UI           :m6c, 2026-11, 2027-01
    M7 高级功能UI + 移动端  :m7c, 2027-01, 2027-03
    M8 优化UI               :m8c, 2027-03, 2027-05
```

## 里程碑总览

| 里程碑 | 主题 | 可见产出 | 详情 |
|--------|------|----------|------|
| [M1](M1.md) | 服务器核心 | 可启动的 FastAPI 服务器 | ✅ 已完成 |
| [M2](M2.md) | MVP | 桌面应用能提交任务、看到 Agent 对话 | ✅ 已完成 |
| [M3](M3.md) | 资源访问 | Agent 能操作本地文件（旧架构） | ✅ 已完成 |
| [M4](M4.md) | 并发 | 多 Agent 并发、worktree 隔离、哈希冲突弹窗 | ✅ 已完成 |
| [M5](M5.md) | MCP 协议 + 认知层 | Client Core MCP Server + 多层记忆 + 事件总线 | |
| [M6](M6.md) | 调度 + 安全 | 智能任务分配 + RBAC + mTLS | |
| [M7](M7.md) | 高级功能 + 移动端 | 全局聊天 + 移动端适配 | |
| [M8](M8.md) | 优化 + 稳定性 | 性能优化 + 稳定性 + 文档 | |
