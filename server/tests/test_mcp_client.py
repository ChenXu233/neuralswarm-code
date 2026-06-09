"""MCP 客户端模块测试"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from neuralswarm.services.mcp.client import McpClient
from neuralswarm.services.mcp.router import McpRouter
from neuralswarm.services.mcp.tools import McpToolRegistry


# ── McpClient 测试 ──────────────────────────────────────────────


class TestMcpClient:
    """McpClient 测试"""

    def test_init(self):
        client = McpClient("ws://localhost:8080/mcp")
        assert client.server_url == "ws://localhost:8080/mcp"
        assert client.websocket is None
        assert client._request_id == 0

    @pytest.mark.asyncio
    async def test_connect_success(self):
        client = McpClient("ws://localhost:8080/mcp")

        with patch("neuralswarm.services.mcp.client.websockets") as mock_ws:
            mock_ws.connect = AsyncMock()
            result = await client.connect()

            assert result is True
            assert client.websocket is not None
            mock_ws.connect.assert_called_once_with("ws://localhost:8080/mcp")

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        client = McpClient("ws://localhost:8080/mcp")

        with patch("neuralswarm.services.mcp.client.websockets") as mock_ws:
            mock_ws.connect = AsyncMock(side_effect=ConnectionError("refused"))
            result = await client.connect()

            assert result is False
            assert client.websocket is None

    @pytest.mark.asyncio
    async def test_disconnect(self):
        client = McpClient("ws://localhost:8080/mcp")
        mock_ws = AsyncMock()
        client.websocket = mock_ws

        await client.disconnect()

        mock_ws.close.assert_called_once()
        assert client.websocket is None

    @pytest.mark.asyncio
    async def test_disconnect_no_connection(self):
        client = McpClient("ws://localhost:8080/mcp")
        # 不应抛出异常
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_list_tools(self):
        client = McpClient("ws://localhost:8080/mcp")
        client.websocket = AsyncMock()

        response = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {"name": "file_read", "description": "Read a file"},
                    {"name": "file_write", "description": "Write a file"},
                ]
            }
        })
        client.websocket.recv = AsyncMock(return_value=response)

        tools = await client.list_tools()

        assert len(tools) == 2
        assert tools[0]["name"] == "file_read"
        assert tools[1]["name"] == "file_write"

    @pytest.mark.asyncio
    async def test_call_tool(self):
        client = McpClient("ws://localhost:8080/mcp")
        client.websocket = AsyncMock()

        response = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": "file contents here"
            }
        })
        client.websocket.recv = AsyncMock(return_value=response)

        result = await client.call_tool("file_read", {"path": "/tmp/test"})

        assert result["content"] == "file contents here"

        # 验证发送的请求格式
        sent = json.loads(client.websocket.send.call_args[0][0])
        assert sent["jsonrpc"] == "2.0"
        assert sent["method"] == "tools/call"
        assert sent["params"]["name"] == "file_read"
        assert sent["params"]["arguments"]["path"] == "/tmp/test"

    @pytest.mark.asyncio
    async def test_request_id_increments(self):
        client = McpClient("ws://localhost:8080/mcp")
        client.websocket = AsyncMock()

        response = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
        client.websocket.recv = AsyncMock(return_value=response)

        await client.list_tools()
        sent1 = json.loads(client.websocket.send.call_args_list[0][0][0])
        assert sent1["id"] == 1

        await client.list_tools()
        sent2 = json.loads(client.websocket.send.call_args_list[1][0][0])
        assert sent2["id"] == 2


# ── McpRouter 测试 ──────────────────────────────────────────────


class TestMcpRouter:
    """McpRouter 测试"""

    def test_register_project(self):
        router = McpRouter()
        router.register_project("proj-1", "client-1")
        assert router.get_client_for_project("proj-1") == "client-1"

    def test_get_client_for_unknown_project(self):
        router = McpRouter()
        assert router.get_client_for_project("unknown") is None

    def test_list_projects_empty(self):
        router = McpRouter()
        assert router.list_projects() == []

    def test_list_projects(self):
        router = McpRouter()
        router.register_project("proj-1", "client-1")
        router.register_project("proj-2", "client-2")
        projects = router.list_projects()
        assert set(projects) == {"proj-1", "proj-2"}

    def test_register_overwrite(self):
        router = McpRouter()
        router.register_project("proj-1", "client-1")
        router.register_project("proj-1", "client-2")
        assert router.get_client_for_project("proj-1") == "client-2"


# ── McpToolRegistry 测试 ────────────────────────────────────────


class TestMcpToolRegistry:
    """McpToolRegistry 测试"""

    def test_register_tool(self):
        registry = McpToolRegistry()

        async def handler(**kwargs):
            return "result"

        registry.register("file_read", "Read a file", handler)

        tool = registry.get_tool("file_read")
        assert tool is not None
        assert tool["name"] == "file_read"
        assert tool["description"] == "Read a file"
        assert tool["handler"] is handler

    def test_get_unknown_tool(self):
        registry = McpToolRegistry()
        assert registry.get_tool("unknown") is None

    def test_list_tools_empty(self):
        registry = McpToolRegistry()
        assert registry.list_tools() == []

    def test_list_tools(self):
        registry = McpToolRegistry()

        async def handler1(**kwargs):
            return "result1"

        async def handler2(**kwargs):
            return "result2"

        registry.register("tool_a", "Tool A", handler1)
        registry.register("tool_b", "Tool B", handler2)

        tools = registry.list_tools()
        assert len(tools) == 2
        # list_tools 不应暴露 handler
        names = {t["name"] for t in tools}
        assert names == {"tool_a", "tool_b"}
        for t in tools:
            assert "handler" not in t
