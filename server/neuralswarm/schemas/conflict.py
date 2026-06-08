from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from neuralswarm.models.enums import ConflictAction, ConflictStatus


class ConflictResponse(BaseModel):
    id: UUID
    task_id: UUID
    file_path: str
    agent_id: UUID
    other_agent_id: UUID
    old_hash: str
    current_hash: str
    current_content: str
    new_content: str
    status: ConflictStatus
    action: ConflictAction | None
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class ConflictDecideRequest(BaseModel):
    action: ConflictAction
