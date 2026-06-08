from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from neuralswarm.models.enums import AgentStatus, AgentType


class AgentResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    agent_type: AgentType
    status: AgentStatus
    task_id: UUID | None
    parent_id: UUID | None
    llm_config: dict
    worktree_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int
