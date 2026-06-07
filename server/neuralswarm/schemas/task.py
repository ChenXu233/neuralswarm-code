from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from neuralswarm.models.enums import TaskStatus


class TaskCreate(BaseModel):
    project_id: UUID
    prompt: str = Field(..., min_length=1)


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    agent_id: UUID
    llm_id: UUID
    status: TaskStatus
    input: str
    output: str | None = None
    error: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
