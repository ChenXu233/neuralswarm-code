import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from neuralswarm.services.bridge import ClientManager
from neuralswarm.api.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Global ClientManager instance
client_manager = ClientManager()


@router.websocket("/ws/client")
async def client_ws(websocket: WebSocket, token: str = Query(...)):
    """Client WebSocket endpoint."""
    # Verify JWT
    try:
        payload = verify_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload["sub"]
    client_id = f"client-{user_id}"

    await websocket.accept()
    await client_manager.register(client_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await client_manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        await client_manager.unregister(client_id)


def get_client_manager() -> ClientManager:
    """Get global ClientManager instance."""
    return client_manager
