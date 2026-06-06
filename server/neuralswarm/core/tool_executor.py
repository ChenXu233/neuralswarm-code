from collections.abc import Callable
from typing import Any


class ToolExecutor:
    """工具执行器，支持动态注册。"""

    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """注册工具。"""
        self._tools[name] = func

    def register_defaults(self):
        """注册内置工具。"""
        from neuralswarm.core.tools import file_read, file_write, shell
        self.register("file_read", file_read)
        self.register("file_write", file_write)
        self.register("shell", shell)

    def list_tools(self) -> list[str]:
        """列出所有已注册工具。"""
        return list(self._tools.keys())

    async def execute(self, tool_name: str, params: dict) -> str:
        """执行工具，返回结果字符串。"""
        tool = self._tools.get(tool_name)
        if tool is None:
            return f"Error: Unknown tool '{tool_name}'. Available: {self.list_tools()}"
        try:
            result = await tool(**params)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"
