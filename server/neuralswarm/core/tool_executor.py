from collections.abc import Callable

from neuralswarm.core.tool_metadata import ToolMetadata


class ToolExecutor:
    """工具执行器，支持动态注册和项目路径上下文。"""

    def __init__(self, project_path: str = ""):
        self._tools: dict[str, Callable] = {}
        self._metadata: dict[str, ToolMetadata] = {}
        self._project_path = project_path

    def register(self, name: str, func: Callable, metadata: ToolMetadata | None = None):
        """注册工具，可选附带元数据。"""
        self._tools[name] = func
        if metadata:
            self._metadata[name] = metadata

    def register_defaults(self):
        """注册内置工具（基于项目路径创建）。"""
        from neuralswarm.core.tools import create_file_ops, create_shell

        (file_read, read_meta), (file_write, write_meta) = create_file_ops(self._project_path)
        shell, shell_meta = create_shell(self._project_path)

        self.register("file_read", file_read, metadata=read_meta)
        self.register("file_write", file_write, metadata=write_meta)
        self.register("shell", shell, metadata=shell_meta)

    def list_tools(self) -> list[str]:
        """列出所有已注册工具。"""
        return list(self._tools.keys())

    def get_metadata(self, name: str) -> ToolMetadata | None:
        """获取工具元数据。"""
        return self._metadata.get(name)

    def get_all_metadata(self) -> list[ToolMetadata]:
        """获取所有工具元数据。"""
        return list(self._metadata.values())

    def to_openai_tools(self) -> list[dict]:
        """转换为 OpenAI function calling 格式。"""
        return [m.to_openai_schema() for m in self._metadata.values()]

    def to_anthropic_tools(self) -> list[dict]:
        """转换为 Anthropic tool use 格式。"""
        return [m.to_anthropic_schema() for m in self._metadata.values()]

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
