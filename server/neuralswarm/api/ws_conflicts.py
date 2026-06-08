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
    """实时推送冲突事件。

    注意：每个 task_id 仅支持一个 WebSocket 订阅者。
    如果已有订阅者，新连接会收到一条提示消息后被关闭。
    """
    manager = get_conflict_manager()

    # 单订阅者模型：如果该 task_id 已有订阅者，拒绝新连接
    if task_id in manager._listeners:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": f"Task {task_id} already has an active conflict subscriber.",
        })
        await websocket.close(code=4000, reason="duplicate subscriber")
        logger.warning(
            "Rejected duplicate conflict subscriber for task %s", task_id
        )
        return

    await websocket.accept()
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
