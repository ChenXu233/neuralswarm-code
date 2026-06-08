from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk
from neuralswarm.models.enums import AgentStatus, AgentType


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    agent_type: Mapped[AgentType] = mapped_column(
        String(20), default=AgentType.WORKER
    )
    status: Mapped[AgentStatus] = mapped_column(
        String(20), default=AgentStatus.IDLE
    )
    task_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )
    tools: Mapped[list] = mapped_column(JSONB, default=list)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    llm_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    worktree_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="agents")
    tasks: Mapped[list["Task"]] = relationship(back_populates="agent", foreign_keys="[Task.agent_id]")
    assigned_task: Mapped["Task | None"] = relationship(
        foreign_keys=[task_id], back_populates="assigned_agent", post_update=True
    )
    parent: Mapped["Agent | None"] = relationship(
        back_populates="children",
        remote_side=[id],
    )
    children: Mapped[list["Agent"]] = relationship(
        back_populates="parent",
    )
