# NeuralSwarm/Code

> **中文**：一个面向项目型代码协作的异构多智能体系统，采用"本地优先 + 可选远程"架构，通过 MCP 协议统一资源访问。

> **English**: A heterogeneous multi-agent collaboration system for project-based code collaboration, featuring a "local-first + optional remote" architecture with unified resource access via MCP protocol.

## ✨ 特性 / Features

- 🏠 **本地优先 + 可选远程** / Local-first + Optional Remote
- 🔌 **MCP 协议统一资源访问** / Unified Resource Access via MCP Protocol
- 🤖 **多智能体并发控制** / Multi-Agent Concurrency Control
- 🧠 **异构 LLM 调度** / Heterogeneous LLM Scheduling
- 🔒 **项目级隔离** / Project-level Isolation

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Python 3.12+
- Node.js 18+
- Rust (for client core)
- Docker (可选 / optional)

### 安装 / Installation

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/ChenXu233/neuralswarm-code.git
cd neuralswarm-code

# 启动服务器 / Start server
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
uvicorn neuralswarm.main:app --reload

# 启动客户端 / Start client
cd client
npm install
npm run dev
```

### Docker 部署 / Docker Deployment

```bash
cd docker
docker-compose up -d
```

## 📖 文档 / Documentation

- [技术架构选型 / Technical Architecture](docs/技术架构选型.md)
- [白皮书 / Whitepaper](docs/白皮书.md)
- [贡献指南 / Contributing Guide](CONTRIBUTING.md)

## 🏗️ 项目结构 / Project Structure

```
neuralswarm-code/
├── client/          # Vue.js 前端 / Vue.js Frontend
├── server/          # Python/FastAPI 后端 / Python/FastAPI Backend
├── desktop/         # Tauri 桌面应用 / Tauri Desktop App
├── core/            # Rust 客户端核心 / Rust Client Core
├── docker/          # Docker 配置 / Docker Configuration
└── docs/            # 文档 / Documentation
```

## 🤝 贡献 / Contributing

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 许可证 / License

Apache 2.0 - 详见 [LICENSE](LICENSE)

## 🙏 致谢 / Acknowledgments

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - Anthropic 推出的工具调用协议标准
- [Tauri](https://tauri.app/) - 跨平台桌面应用框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
