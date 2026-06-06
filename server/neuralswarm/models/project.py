from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
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
    agents: Mapped[list["Agent"]] = relationship(back_populates="project")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
    memories: Mapped[list["ProjectMemory"]] = relationship(back_populates="project")
