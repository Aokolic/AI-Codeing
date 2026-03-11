"""DataFeed ORM model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FeedType(str, enum.Enum):
    rss = "rss"
    api = "api"
    scraper = "scraper"


class FeedStatus(str, enum.Enum):
    normal = "normal"
    warning = "warning"
    offline = "offline"


class DataFeed(Base):
    __tablename__ = "data_feeds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    feed_type: Mapped[FeedType] = mapped_column(Enum(FeedType), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    parse_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    schedule_cron: Mapped[str] = mapped_column(String(50), nullable=False, default="*/30 * * * *")
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[FeedStatus] = mapped_column(
        Enum(FeedStatus), nullable=False, default=FeedStatus.normal
    )
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sources: Mapped[list["Source"]] = relationship("Source", back_populates="data_feed")  # noqa: F821
