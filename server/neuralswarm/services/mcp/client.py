"""MCP 客户端 - 连接 MCP Server"""

import json
import logging
from typing import Any

import websockets

logger = logging.getLogger(__name__)


class McpClient:
    """MCP 客户端"""

    def __init__(self, server_url: str):
        self.server_url = server_url
        self.websocket = None
        self._request_id = 0

    async def connect(self) -> bool:
        """连接 MCP Server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info("Connected to MCP Server: %s", self.server_url)
            return True
        except Exception as e:
            logger.error("MCP connection error: %s", e)
            return False

    async def disconnect(self) -> None:
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from MCP Server")

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出可用工具"""
        response = await self._send_request("tools/list", {})
        return response.get("tools", [])

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """调用工具"""
        response = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return response

    async def _send_request(
        self,
        method: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """发送 JSON-RPC 请求"""
        self._request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }

        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()

        return json.loads(response).get("result", {})
