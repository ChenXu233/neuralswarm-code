import os

import aiofiles

from neuralswarm.core.tool_metadata import ToolMetadata, ToolParameter


def create_file_ops(project_path: str):
    """创建文件操作工具，绑定项目路径。"""

    def _resolve(path: str) -> str:
        """相对路径基于 project_path 解析，绝对路径直接返回。"""
        if os.path.isabs(path):
            return path
        return os.path.join(project_path, path)

    async def file_read(path: str) -> str:
        """读取文件内容。"""
        resolved = _resolve(path)
        try:
            async with aiofiles.open(resolved, "r") as f:
                return await f.read()
        except Exception as e:
            return f"Error reading file '{path}': {e}"

    async def file_write(path: str, content: str) -> str:
        """写入文件。"""
        resolved = _resolve(path)
        try:
            os.makedirs(os.path.dirname(resolved), exist_ok=True)
            async with aiofiles.open(resolved, "w") as f:
                await f.write(content)
            return f"Successfully written to '{path}'"
        except Exception as e:
            return f"Error writing file '{path}': {e}"

    read_meta = ToolMetadata(
        name="file_read",
        description="Read file content. Supports relative paths (resolved from project directory) and absolute paths.",
        parameters=[
            ToolParameter(name="path", type="string", description="File path (relative to project or absolute)"),
        ],
    )

    write_meta = ToolMetadata(
        name="file_write",
        description="Write content to file. Creates parent directories if needed. Supports relative and absolute paths.",
        parameters=[
            ToolParameter(name="path", type="string", description="File path (relative to project or absolute)"),
            ToolParameter(name="content", type="string", description="Content to write"),
        ],
    )

    return (file_read, read_meta), (file_write, write_meta)
