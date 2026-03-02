"""EventNode ORM model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventNode(Base):
    __tablename__ = "event_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Embeddings stored as JSON array (768-dim float list) for SQLite compat;
    # for PostgreSQL, consider pgvector extension in a future migration.
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="events")  # noqa: F821
    event_sources: Mapped[list["EventNodeSource"]] = relationship(  # noqa: F821
        "EventNodeSource", back_populates="event_node", cascade="all, delete-orphan"
    )
    credibility_assessments: Mapped[list["CredibilityAssessment"]] = relationship(  # noqa: F821
        "CredibilityAssessment", back_populates="event_node", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_event_case_time", "case_id", "event_time"),
        Index("idx_event_time", "event_time"),
    )
