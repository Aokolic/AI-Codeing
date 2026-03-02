"""CredibilityAssessment ORM model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CredibilityLevel(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unverified = "unverified"


class CredibilityAssessment(Base):
    __tablename__ = "credibility_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_nodes.id", ondelete="CASCADE"), nullable=False
    )
    level: Mapped[CredibilityLevel] = mapped_column(Enum(CredibilityLevel), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    authority_score: Mapped[float] = mapped_column(Float, nullable=False)
    timeliness_score: Mapped[float] = mapped_column(Float, nullable=False)
    cross_verify_score: Mapped[float] = mapped_column(Float, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    conflict_sources_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    event_node: Mapped["EventNode"] = relationship(  # noqa: F821
        "EventNode", back_populates="credibility_assessments"
    )
