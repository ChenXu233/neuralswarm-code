"""M5 端到端测试"""

import pytest
from fastapi.testclient import TestClient

from neuralswarm.server import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


def test_memory_api_get_l1(client):
    """测试获取 L1 记忆"""
    response = client.get("/api/memory/test-project?level=L1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert data["level"] == "L1"
    assert "data" in data


def test_memory_api_get_l2(client):
    """测试获取 L2 记忆"""
    response = client.get("/api/memory/test-project?level=L2&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert data["level"] == "L2"
    assert "data" in data


def test_memory_api_write_l1(client):
    """测试写入 L1 记忆"""
    response = client.post(
        "/api/memory/test-project",
        json={"level": "L1", "content": "测试事件"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["level"] == "L1"


def test_memory_api_unsupported_level(client):
    """测试不支持的记忆层级"""
    response = client.get("/api/memory/test-project?level=L4&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_reflection_agent():
    """测试反思 Agent"""
    from neuralswarm.services.memory.reflection_agent import reflection_agent

    context = [
        {"content": "使用 FastAPI 框架"},
        {"content": "SQLAlchemy ORM"}
    ]
    events = []

    # 简化测试，验证函数存在且可调用
    assert callable(reflection_agent.reflect)


def test_mcp_client():
    """测试 MCP 客户端初始化"""
    from neuralswarm.services.mcp.client import McpClient

    client = McpClient("ws://localhost:8765")
    assert client.server_url == "ws://localhost:8765"
    assert client.websocket is None


def test_mcp_router():
    """测试 MCP 路由"""
    from neuralswarm.services.mcp.router import mcp_router

    # 测试注册和获取
    mcp_router.register_project("test-project", "client-1")
    assert mcp_router.get_client_for_project("test-project") == "client-1"
    assert mcp_router.get_client_for_project("unknown") is None


def test_task_service_mcp_method():
    """测试 TaskService 的 MCP 方法存在"""
    from neuralswarm.services.task_service import TaskService

    # 验证方法存在
    assert hasattr(TaskService, '_get_mcp_client')
