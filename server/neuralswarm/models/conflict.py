from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neuralswarm.models.base import Base, uuid7_pk
from neuralswarm.models.enums import ConflictAction, ConflictStatus


class Conflict(Base):
    __tablename__ = "conflicts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    file_path: Mapped[str] = mapped_column(String(1024))
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    other_agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    old_hash: Mapped[str] = mapped_column(String(64))
    current_hash: Mapped[str] = mapped_column(String(64))
    current_content: Mapped[str] = mapped_column(Text)
    new_content: Mapped[str] = mapped_column(Text)
    status: Mapped[ConflictStatus] = mapped_column(
        String(20), default=ConflictStatus.PENDING
    )
    action: Mapped[ConflictAction | None] = mapped_column(
        String(30), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
