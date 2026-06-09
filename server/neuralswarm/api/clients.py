# server/neuralswarm/api/clients.py
"""Client status API."""
from typing import Any
from fastapi import APIRouter, Depends
from neuralswarm.services.bridge.client_manager import ClientManager
from neuralswarm.api.ws_client import get_client_manager

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("")
async def list_clients():
    """List connected clients."""
    cm = get_client_manager()
    client_ids = cm.list_clients()
    return {
        "items": [{"id": cid, "status": "online"} for cid in client_ids],
        "total": len(client_ids),
    }


@router.get("/{client_id}")
async def get_client(client_id: str):
    """Get client status."""
    cm = get_client_manager()
    if cm.is_connected(client_id):
        return {"data": {"id": client_id, "status": "online"}}
    return {"data": {"id": client_id, "status": "offline"}}


@router.post("/connect")
async def connect_client(
    client_id: str,
    token: str
) -> dict[str, Any]:
    """客户端连接服务器"""
    # 验证 token
    # 注册客户端
    # 返回连接确认
    return {"status": "connected", "client_id": client_id}
