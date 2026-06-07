import asyncio
import logging
from fastapi import WebSocket

from neuralswarm.services.bridge.protocol import ExecuteCommand, CommandResult

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages client WebSocket connections."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._pending: dict[str, asyncio.Future] = {}

    async def register(self, client_id: str, ws: WebSocket):
        self._connections[client_id] = ws
        logger.info(f"Client registered: {client_id}")

    async def unregister(self, client_id: str):
        self._connections.pop(client_id, None)
        logger.info(f"Client unregistered: {client_id}")

    def is_connected(self, client_id: str) -> bool:
        return client_id in self._connections

    def list_clients(self) -> list[str]:
        return list(self._connections.keys())

    async def execute(self, client_id: str, command: str, params: dict, timeout: int = 30) -> dict:
        ws = self._connections.get(client_id)
        if not ws:
            raise RuntimeError(f"Client {client_id} not connected")

        cmd = ExecuteCommand(command=command, params=params)
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[cmd.request_id] = future

        try:
            await ws.send_json(cmd.to_json())
            result = await asyncio.wait_for(future, timeout=timeout)
            if result.status == "error":
                raise RuntimeError(result.data.get("message", "Client execution failed"))
            return result.data
        finally:
            self._pending.pop(cmd.request_id, None)

    async def handle_message(self, client_id: str, data: dict):
        if data.get("type") == "result":
            result = CommandResult.from_json(data)
            future = self._pending.pop(result.request_id, None)
            if future and not future.done():
                future.set_result(result)
