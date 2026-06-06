from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk
from neuralswarm.models.enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    llm_id: Mapped[UUID] = mapped_column(ForeignKey("llms.id"))
    status: Mapped[TaskStatus] = mapped_column(
        String(20), default=TaskStatus.PENDING
    )
    input: Mapped[str] = mapped_column(Text)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="tasks")
    agent: Mapped["Agent"] = relationship(back_populates="tasks")
    llm: Mapped["LLM"] = relationship()
