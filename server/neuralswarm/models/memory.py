from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk
from neuralswarm.models.enums import MemoryLevel


class ProjectMemory(Base):
    __tablename__ = "project_memories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    agent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )
    level: Mapped[MemoryLevel] = mapped_column(String(5))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[dict] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="memories")
    agent: Mapped["Agent | None"] = relationship()


class GlobalMemory(Base):
    __tablename__ = "global_memories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
