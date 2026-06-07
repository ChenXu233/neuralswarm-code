"""Bridge Router tool factory for local projects."""
from neuralswarm.core.tool_metadata import ToolMetadata, ToolParameter


def create_bridge_file_ops(bridge, project_uri: str):
    """Create file operations tools backed by Bridge Router."""

    def _resolve(path: str) -> str:
        if path.startswith("server://") or path.startswith("client://"):
            return path
        return f"{project_uri.rstrip('/')}/{path.lstrip('/')}"

    async def file_read(path: str) -> str:
        uri = _resolve(path)
        return await bridge.read(uri)

    async def file_write(path: str, content: str) -> str:
        uri = _resolve(path)
        return await bridge.write(uri, content)

    read_meta = ToolMetadata(
        name="file_read",
        description="Read file content from client machine.",
        parameters=[
            ToolParameter(name="path", type="string", description="File path"),
        ],
    )

    write_meta = ToolMetadata(
        name="file_write",
        description="Write content to file on client machine.",
        parameters=[
            ToolParameter(name="path", type="string", description="File path"),
            ToolParameter(name="content", type="string", description="Content to write"),
        ],
    )

    return (file_read, read_meta), (file_write, write_meta)


def create_bridge_shell(bridge, project_uri: str):
    """Create shell tool backed by Bridge Router."""

    async def shell(command: str, timeout: int = 30) -> str:
        return await bridge.shell(project_uri, command, timeout=timeout)

    meta = ToolMetadata(
        name="shell",
        description="Execute shell command on client machine.",
        parameters=[
            ToolParameter(name="command", type="string", description="Shell command"),
            ToolParameter(name="timeout", type="integer", description="Timeout in seconds", required=False),
        ],
    )

    return shell, meta
