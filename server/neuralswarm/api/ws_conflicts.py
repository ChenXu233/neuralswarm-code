import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import UUID

from neuralswarm.api.conflicts import get_conflict_manager
from neuralswarm.schemas.conflict import ConflictResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/conflicts/{task_id}")
async def conflict_events(websocket: WebSocket, task_id: UUID):
    """实时推送冲突事件。"""
    await websocket.accept()

    manager = get_conflict_manager()
    queue = manager.subscribe(task_id)

    try:
        while True:
            try:
                conflict = await asyncio.wait_for(queue.get(), timeout=30.0)
                data = ConflictResponse.model_validate(conflict).model_dump(
                    mode="json"
                )
                await websocket.send_json({"type": "conflict", "data": data})
            except asyncio.TimeoutError:
                # 发送心跳
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error for task %s", task_id)
    finally:
        manager.unsubscribe(task_id)
