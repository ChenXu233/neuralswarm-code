from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralswarm.models.base import Base, uuid7_pk


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    action: Mapped[str] = mapped_column(String(100))
    resource: Mapped[str] = mapped_column(String(1024))
    detail: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    agent: Mapped["Agent"] = relationship()
