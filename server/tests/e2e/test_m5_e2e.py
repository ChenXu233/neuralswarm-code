"""M5 端到端测试 - 完整流程"""

import asyncio

import pytest
from fastapi.testclient import TestClient

from neuralswarm.server import app
from neuralswarm.services.memory.l0_memory import l0_memory
from neuralswarm.services.memory.l1_memory import l1_memory, Event
from neuralswarm.services.memory.l2_memory import l2_memory
from neuralswarm.services.memory.l3_memory import l3_memory
from neuralswarm.services.memory.reflection_agent import reflection_agent
from neuralswarm.services.event_bus import event_bus
from neuralswarm.services.mcp.router import mcp_router


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


# ---------------------------------------------------------------------------
# 辅助：在同步测试中运行协程
# ---------------------------------------------------------------------------
def _run(coro):
    """在同步测试中运行一个协程并返回结果。"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


# =========================================================================
# 记忆流程
# =========================================================================
class TestMemoryFlow:
    """测试记忆流程"""

    def test_full_memory_lifecycle(self, client):
        """测试完整的记忆生命周期"""
        project_id = "e2e-project"

        # 1. 写入 L1 事件
        response = client.post(
            f"/api/memory/{project_id}",
            json={"level": "L1", "content": "创建了 FastAPI 项目"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        # 2. 写入更多 L1 事件
        client.post(
            f"/api/memory/{project_id}",
            json={"level": "L1", "content": "添加了用户认证"},
        )

        # 3. 获取 L1 记忆
        response = client.get(f"/api/memory/{project_id}?level=L1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "L1"
        assert len(data["data"]) == 2

    def test_l2_knowledge_generation(self, client):
        """测试 L2 知识生成"""
        project_id = "e2e-project-l2"

        # 1. 存储 L2 知识
        _run(
            l2_memory.store_knowledge(
                project_id=project_id,
                content="项目使用 FastAPI + SQLAlchemy",
                source="reflection_agent",
                metadata={"topic": "architecture"},
            )
        )

        # 2. 获取 L2 记忆
        response = client.get(f"/api/memory/{project_id}?level=L2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "L2"
        assert len(data["data"]) > 0
        assert "FastAPI" in data["data"][0]["content"]


# =========================================================================
# 事件总线流程
# =========================================================================
class TestEventBusFlow:
    """测试事件总线流程"""

    def test_event_publish_subscribe(self):
        """测试事件发布和订阅"""
        received = []

        async def handler(event):
            received.append(event)

        async def run_test():
            # 订阅事件
            sub = await event_bus.subscribe("test:e2e", handler)

            # 发布事件
            await event_bus.publish("test:e2e", {"data": "test"})

            # 验证
            assert len(received) == 1
            assert received[0]["data"] == "test"

            # 取消订阅
            await event_bus.unsubscribe(sub)

            # 再次发布
            await event_bus.publish("test:e2e", {"data": "test2"})
            assert len(received) == 1  # 不应该收到新事件

        _run(run_test())


# =========================================================================
# MCP 路由流程
# =========================================================================
class TestMcpRouterFlow:
    """测试 MCP 路由流程"""

    def test_project_registration_and_lookup(self):
        """测试项目注册和查找"""
        # 注册项目
        mcp_router.register_project("e2e-project", "client-1")
        mcp_router.register_project("e2e-project-2", "client-2")

        # 查找
        assert mcp_router.get_client_for_project("e2e-project") == "client-1"
        assert mcp_router.get_client_for_project("e2e-project-2") == "client-2"
        assert mcp_router.get_client_for_project("unknown") is None

        # 列出项目
        projects = mcp_router.list_projects()
        assert "e2e-project" in projects
        assert "e2e-project-2" in projects


# =========================================================================
# 反思 Agent 流程
# =========================================================================
class TestReflectionAgentFlow:
    """测试反思 Agent 流程"""

    def test_reflection_generates_knowledge(self):
        """测试反思生成知识"""
        project_id = "e2e-reflection"

        async def run_test():
            # 准备上下文和事件
            context = [
                {"content": "使用 FastAPI 框架"},
                {"content": "SQLAlchemy ORM"},
                {"content": "PostgreSQL 数据库"},
            ]

            events = [
                Event(event_type="file_create", detail="创建了 main.py", project_id=project_id),
                Event(event_type="file_create", detail="创建了 models.py", project_id=project_id),
            ]

            # 执行反思
            result = await reflection_agent.reflect(project_id, context, events)

            # 验证
            assert result is not None
            assert "FastAPI" in result.get("content", "") or "SQLAlchemy" in result.get("content", "")

            # 验证 L2 知识已存储
            knowledge = await l2_memory.get_all_knowledge(project_id)
            assert len(knowledge) > 0

        _run(run_test())


# =========================================================================
# L0 记忆流程
# =========================================================================
class TestL0MemoryFlow:
    """测试 L0 记忆流程"""

    def test_context_save_load_compact(self):
        """测试上下文保存、加载、压缩"""
        agent_id = "e2e-agent"

        async def run_test():
            # 保存上下文
            context = [
                {"role": "user", "content": "Message 1"},
                {"role": "assistant", "content": "Response 1"},
                {"role": "user", "content": "Message 2"},
                {"role": "assistant", "content": "Response 2"},
                {"role": "user", "content": "Message 3"},
                {"role": "assistant", "content": "Response 3"},
            ]

            await l0_memory.save_context(agent_id, context)

            # 加载上下文
            loaded = await l0_memory.load_context(agent_id)
            assert loaded == context

            # 压缩上下文
            compacted = await l0_memory.compact_context(agent_id, keep_last=2)
            assert len(compacted) == 2
            assert compacted[-1]["content"] == "Response 3"

            # 再次加载
            loaded = await l0_memory.load_context(agent_id)
            assert len(loaded) == 2

        _run(run_test())
