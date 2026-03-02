"""Source and EventNodeSource ORM models."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SourceType(str, enum.Enum):
    government = "government"
    mainstream_media = "mainstream_media"
    academic = "academic"
    local_media = "local_media"
    social_media = "social_media"
    unknown = "unknown"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    reputation_score: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    has_false_history: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_feed_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("data_feeds.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    data_feed: Mapped["DataFeed | None"] = relationship("DataFeed", back_populates="sources")  # noqa: F821
    event_sources: Mapped[list["EventNodeSource"]] = relationship(
        "EventNodeSource", back_populates="source", cascade="all, delete-orphan"
    )


class EventNodeSource(Base):
    __tablename__ = "event_node_sources"

    event_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_nodes.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    event_node: Mapped["EventNode"] = relationship("EventNode", back_populates="event_sources")  # noqa: F821
    source: Mapped["Source"] = relationship("Source", back_populates="event_sources")


# Avoid circular import — DataFeed is defined in data_feed.py; the relationship
# is back-populated from there.
Source.data_feed  # noqa: B018 — triggers lazy relationship resolution only
