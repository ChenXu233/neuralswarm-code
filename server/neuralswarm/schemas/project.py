from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1, max_length=1024)
    project_type: str = Field(default="cloud", pattern="^(cloud|local)$")
    client_id: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    path: str
    project_type: str
    client_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
