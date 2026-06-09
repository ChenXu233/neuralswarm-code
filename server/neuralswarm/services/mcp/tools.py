"""MCP 工具注册"""

import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class McpToolRegistry:
    """MCP 工具注册表"""

    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}

    def register(self, name: str, description: str, handler: Callable[..., Awaitable[Any]]) -> None:
        """注册工具"""
        self._tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
        logger.debug("Registered MCP tool: %s", name)

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """列出所有工具"""
        return [
            {"name": t["name"], "description": t["description"]}
            for t in self._tools.values()
        ]


# 全局 MCP 工具注册表
mcp_tool_registry = McpToolRegistry()
