from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.config import settings
from neuralswarm.database import get_db
from neuralswarm.models.task import Task
from neuralswarm.models.enums import TaskStatus
from neuralswarm.schemas.task import TaskCreate, TaskListResponse, TaskResponse
from neuralswarm.services.llm.gateway import LLMGateway
from neuralswarm.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_task_service(db: AsyncSession) -> TaskService:
    gateway = LLMGateway(base_url=settings.LLM_GATEWAY_URL, api_key=settings.LLM_GATEWAY_API_KEY, timeout=settings.LLM_GATEWAY_TIMEOUT)
    return TaskService(db=db, llm_gateway=gateway)


@router.post("")
async def create_task(body: TaskCreate, db: AsyncSession = Depends(get_db)):
    service = _get_task_service(db)
    try:
        task = await service.submit_task(project_id=body.project_id, prompt=body.prompt)
        return {"data": TaskResponse.model_validate(task).model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}")
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": TaskResponse.model_validate(task).model_dump()}


@router.get("")
async def list_tasks(
    project_id: UUID | None = Query(None),
    status: TaskStatus | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.deleted_at.is_(None))
    count_stmt = select(func.count()).select_from(Task).where(Task.deleted_at.is_(None))

    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
        count_stmt = count_stmt.where(Task.project_id == project_id)
    if status:
        stmt = stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)

    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.offset(offset).limit(limit).order_by(Task.created_at.desc())
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return {
        "items": [TaskResponse.model_validate(t).model_dump() for t in tasks],
        "total": total,
    }


@router.delete("/{task_id}")
async def cancel_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    service = _get_task_service(db)
    try:
        task = await service.cancel_task(task_id)
        return {"data": TaskResponse.model_validate(task).model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
