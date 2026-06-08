from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.database import get_db
from neuralswarm.models.agent import Agent
from neuralswarm.models.enums import AgentStatus, AgentType
from neuralswarm.schemas.agent import AgentListResponse, AgentResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/{agent_id}")
async def get_agent(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取单个 Agent 详情。"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"data": AgentResponse.model_validate(agent).model_dump()}


@router.get("")
async def list_agents(
    project_id: UUID | None = Query(None),
    status: AgentStatus | None = Query(None),
    agent_type: AgentType | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """列出所有 Agent，支持按项目、状态、类型筛选。"""
    stmt = select(Agent).where(Agent.deleted_at.is_(None))
    count_stmt = select(func.count()).select_from(Agent).where(Agent.deleted_at.is_(None))

    if project_id:
        stmt = stmt.where(Agent.project_id == project_id)
        count_stmt = count_stmt.where(Agent.project_id == project_id)
    if status:
        stmt = stmt.where(Agent.status == status)
        count_stmt = count_stmt.where(Agent.status == status)
    if agent_type:
        stmt = stmt.where(Agent.agent_type == agent_type)
        count_stmt = count_stmt.where(Agent.agent_type == agent_type)

    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.offset(offset).limit(limit).order_by(Agent.created_at.desc())
    result = await db.execute(stmt)
    agents = result.scalars().all()

    return AgentListResponse(
        items=[AgentResponse.model_validate(a) for a in agents],
        total=total,
    ).model_dump()
