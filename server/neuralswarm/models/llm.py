from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from neuralswarm.models.base import Base, uuid7_pk


class LLM(Base):
    __tablename__ = "llms"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7_pk)
    model_id: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))
    gateway_route: Mapped[str] = mapped_column(String(255))
    capabilities: Mapped[dict] = mapped_column(JSONB, default=dict)
    cost_tier: Mapped[str] = mapped_column(String(20))
    rate_limit: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_free_tier: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
