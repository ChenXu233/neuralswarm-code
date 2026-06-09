"""记忆 API"""

from fastapi import APIRouter, Query
from typing import Any

from neuralswarm.services.memory.l1_memory import l1_memory
from neuralswarm.services.memory.l2_memory import l2_memory
from neuralswarm.services.memory.l3_memory import l3_memory

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("/{project_id}")
async def get_memory(
    project_id: str,
    level: str = Query(..., description="记忆层级: L1, L2, L3"),
    limit: int = Query(100, description="返回数量")
) -> dict[str, Any]:
    """获取记忆"""
    if level == "L1":
        events = await l1_memory.get_events(project_id, limit)
        return {"level": "L1", "data": [{"event": e.event_type, "detail": e.detail} for e in events]}
    elif level == "L2":
        knowledge = await l2_memory.get_all_knowledge(project_id)
        return {"level": "L2", "data": [{"content": k.content, "source": k.source} for k in knowledge]}
    else:
        return {"error": f"Unsupported level: {level}"}


@router.post("/{project_id}")
async def write_memory(
    project_id: str,
    data: dict[str, Any]
) -> dict[str, Any]:
    """写入记忆"""
    level = data.get("level")
    content = data.get("content")

    if level == "L1":
        event = await l1_memory.record_event(project_id, "manual", content)
        return {"status": "ok", "level": "L1", "event_id": id(event)}
    else:
        return {"error": f"Write not supported for level: {level}"}
