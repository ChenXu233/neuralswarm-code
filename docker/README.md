# NeuralSwarm Docker 部署

NeuralSwarm v2.0 节点分两种角色：

| 节点类型 | 说明 | 包含 |
|---------|------|------|
| **user-neuron** | 用户神经元，带 Web UI | 内核 + 前端界面 |
| **compute-neuron** | 计算神经元，纯后台服务 | 仅内核，无 UI |

两者运行同一个 Rust 二进制，通过 Dockerfile 的 `target` 区分构建阶段。

---

## 用户神经元部署

```bash
# 构建并启动
docker compose up -d user-neuron

# 查看日志
docker compose logs -f user-neuron

# 访问 http://localhost:8000
```

带前端界面的完整节点。浏览器访问即可使用。

## 计算神经元部署

```bash
# 构建并启动（无 UI）
docker compose up -d compute-neuron

# 访问 http://localhost:8001（API 端口）
```

纯内核节点，适合作为 GPU 计算节点或远程执行节点部署在服务器上。

## 多节点组域

多台机器组一个信任域（逻辑计算机）：

```bash
# 节点 A（用户神经元，作为 bootstrap）
NS_BOOTSTRAP= NS_PEER_PORT=9090 docker compose up -d user-neuron

# 节点 B（计算神经元，发现节点 A）
NS_BOOTSTRAP=/ip4/<NODE_A_IP>/tcp/9090 NS_PEER_PORT=9091 docker compose up -d compute-neuron
```

域内自动 Gossip 同步，从节点 A 的 UI 可操作节点 B 的项目。

## 开发模式

前端热重载 + 容器内内核：

```bash
docker compose --profile dev up -d kernel-dev
cd ../client && npm run dev
```

前端通过 Vite dev server (`http://localhost:5173`) 访问，API 代理到内核 (`http://localhost:8000`)。

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NS_PORT` | `8000` | HTTP 服务端口 |
| `NS_LOG` | `info` | 日志级别 |
| `NS_DATA_DIR` | `/data` | SQLite 数据目录 |
| `NS_LLM_ENDPOINT` | — | LLM API 端点 |
| `NS_LLM_API_KEY` | — | LLM API 密钥 |
| `NS_LLM_MODEL` | — | LLM 模型名 |
| `NS_PEER_PORT` | `9090` | P2P 节点发现端口 |
| `NS_BOOTSTRAP` | — | 初始节点地址（空 = 自举） |
