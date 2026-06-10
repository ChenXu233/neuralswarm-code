# 贡献指南 / Contributing Guide

感谢你对 NeuralSwarm/Code 的兴趣！我们欢迎各种形式的贡献。

Thank you for your interest in NeuralSwarm/Code! We welcome contributions of all kinds.

## 开发环境搭建 / Development Setup

### 服务器 (Python)

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 客户端 (Vue.js)

```bash
cd client
npm install
npm run dev
```

### 桌面端 (Tauri)

```bash
cd desktop
npm install
npm run tauri dev
```

## 代码规范 / Code Standards

### Python

- 使用 [Ruff](https://github.com/astral-sh/ruff) 进行 linting
- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 代码风格
- 必须添加类型注解
- 运行 linting：`cd server && ruff check .`

### TypeScript/Vue

- 使用 ESLint + Prettier
- 使用 Vue 3 Composition API
- 运行类型检查：`cd client && npx vue-tsc --noEmit`

## 提交规范 / Commit Convention

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <description>

[optional body]

[optional footer(s)]
```

**类型 / Types:**

- `feat`: 新功能 / New feature
- `fix`: 修复 bug / Bug fix
- `docs`: 文档更新 / Documentation update
- `style`: 代码格式（不影响功能）/ Code formatting (no functional change)
- `refactor`: 重构 / Refactoring
- `test`: 测试相关 / Tests
- `chore`: 构建/工具相关 / Build/tooling

**示例 / Examples:**

```
feat: add user authentication
fix: resolve memory leak in agent runtime
docs: update API documentation
```

## Pull Request 流程 / Pull Request Process

1. **Fork 仓库** / Fork the repository

2. **创建特性分支** / Create a feature branch
   ```bash
   git checkout -b feat/my-feature
   ```

3. **提交更改** / Commit your changes
   ```bash
   git commit -m "feat: add my feature"
   ```

4. **推送分支** / Push to the branch
   ```bash
   git push origin feat/my-feature
   ```

5. **创建 Pull Request** / Create a Pull Request
   - 填写 PR 模板 / Fill out the PR template
   - 关联相关 Issue / Link related issues
   - 等待代码审查 / Wait for code review

## 问题反馈 / Reporting Issues

### Bug 报告 / Bug Reports

使用 [Bug 报告模板](https://github.com/ChenXu233/neuralswarm-code/issues/new?template=bug_report.md) 创建 Issue。

Use the [Bug Report template](https://github.com/ChenXu233/neuralswarm-code/issues/new?template=bug_report.md) to create an issue.

### 功能请求 / Feature Requests

使用 [功能请求模板](https://github.com/ChenXu233/neuralswarm-code/issues/new?template=feature_request.md) 创建 Issue。

Use the [Feature Request template](https://github.com/ChenXu233/neuralswarm-code/issues/new?template=feature_request.md) to create an issue.

### 安全问题 / Security Issues

安全问题请参考 [SECURITY.md](SECURITY.md)，**不要**公开 Issue。

For security issues, please refer to [SECURITY.md](SECURITY.md). Do **NOT** create public issues.

## 行为准则 / Code of Conduct

请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 了解社区行为准则。

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines.

## 获取帮助 / Getting Help

- 提交 Issue / Create an issue
- 参与讨论 / Join discussions

感谢你的贡献！/ Thank you for your contribution!
