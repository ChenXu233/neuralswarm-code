import json
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from neuralswarm.services.redis import redis_client

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/tasks/{task_id}")
async def task_events_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()

    # Send historical events (reconnection catch-up)
    history = await redis_client.get_events_since(task_id, "0")
    for event in history:
        await websocket.send_json(event)

    # Subscribe to real-time events
    pubsub = await redis_client.subscribe(task_id)

    try:
        while True:
            # Check for client messages (last_event_id for reconnection)
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                data = json.loads(msg)
                if "last_event_id" in data:
                    events = await redis_client.get_events_since(task_id, data["last_event_id"])
                    for event in events:
                        await websocket.send_json(event)
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

            # Check Redis events
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message["type"] == "message":
                event = json.loads(message["data"])
                await websocket.send_json(event)

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"task:{task_id}")
        await pubsub.aclose()
