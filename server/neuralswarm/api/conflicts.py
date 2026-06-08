from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.database import get_db
from neuralswarm.models.conflict import Conflict
from neuralswarm.models.enums import ConflictAction, ConflictStatus
from neuralswarm.schemas.conflict import ConflictDecideRequest, ConflictResponse

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])

# 全局 ConflictManager 实例（延迟初始化）
_conflict_manager = None


def get_conflict_manager():
    global _conflict_manager
    if _conflict_manager is None:
        from neuralswarm.core.concurrency.conflict_manager import ConflictManager
        _conflict_manager = ConflictManager()
    return _conflict_manager


@router.get("/{conflict_id}")
async def get_conflict(conflict_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取冲突详情。"""
    conflict = await db.get(Conflict, conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"data": ConflictResponse.model_validate(conflict).model_dump()}


@router.post("/{conflict_id}/decide")
async def decide_conflict(
    conflict_id: UUID,
    body: ConflictDecideRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户决策冲突解决方案。"""
    conflict = await db.get(Conflict, conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    if conflict.status != ConflictStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail=f"Conflict already {conflict.status}",
        )

    from datetime import datetime, timezone

    conflict.status = ConflictStatus.RESOLVED
    conflict.action = body.action
    conflict.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(conflict)

    # 同步更新 ConflictManager 内存状态
    manager = get_conflict_manager()
    if conflict.id in manager.pending_conflicts:
        await manager.resolve(conflict.id, body.action)

    return {"data": ConflictResponse.model_validate(conflict).model_dump()}
