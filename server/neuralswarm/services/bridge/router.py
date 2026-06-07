import logging
from urllib.parse import urlparse

from neuralswarm.services.bridge.client_manager import ClientManager

logger = logging.getLogger(__name__)


class BridgeRouter:
    """Routes resource requests based on URI prefix."""

    def __init__(self, client_manager: ClientManager):
        self._client_manager = client_manager

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parse URI, returns (type, path). type: 'local' or client_id."""
        parsed = urlparse(uri)
        if parsed.scheme == "server":
            return "local", parsed.path
        elif parsed.scheme == "client":
            return parsed.hostname or "", parsed.path
        else:
            raise ValueError(f"Unknown URI scheme: {parsed.scheme}")

    async def read(self, uri: str) -> str:
        node_type, path = self._parse_uri(uri)
        if node_type == "local":
            from neuralswarm.core.tools.file_ops import create_file_ops
            file_read, _ = create_file_ops("")
            return await file_read(path)
        else:
            result = await self._client_manager.execute(
                node_type, "file_read", {"path": path}
            )
            return result.get("content", "")

    async def write(self, uri: str, content: str) -> str:
        node_type, path = self._parse_uri(uri)
        if node_type == "local":
            from neuralswarm.core.tools.file_ops import create_file_ops
            _, file_write = create_file_ops("")
            return await file_write(path, content)
        else:
            result = await self._client_manager.execute(
                node_type, "file_write", {"path": path, "content": content}
            )
            return result.get("message", "Written")

    async def shell(self, uri: str, command: str, timeout: int = 30) -> str:
        node_type, path = self._parse_uri(uri)
        if node_type == "local":
            from neuralswarm.core.tools.shell import create_shell
            shell_func = create_shell(path)
            return await shell_func(command, timeout=timeout)
        else:
            result = await self._client_manager.execute(
                node_type, "shell", {"command": command, "timeout": timeout}
            )
            return result.get("output", "")
