from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk
from neuralswarm.models.enums import LockMode


class Lock(Base):
    __tablename__ = "locks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    resource_uri: Mapped[str] = mapped_column(String(1024))
    holder_agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    mode: Mapped[LockMode] = mapped_column(String(5))
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    holder: Mapped["Agent"] = relationship()
