"""DataFeed Pydantic schemas."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.data_feed import FeedStatus, FeedType


class DataFeedOut(BaseModel):
    id: str
    name: str
    feed_type: FeedType
    url: str
    status: FeedStatus
    consecutive_failures: int
    last_collected_at: Optional[datetime] = None
    schedule_cron: str
    created_at: datetime
    is_builtin: bool = False

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _ensure_utc(self) -> "DataFeedOut":
        for field in ("last_collected_at", "created_at"):
            val = getattr(self, field)
            if val is not None and val.tzinfo is None:
                object.__setattr__(self, field, val.replace(tzinfo=timezone.utc))
        return self


class DataFeedCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    feed_type: FeedType
    url: str = Field(..., min_length=10)
    schedule_cron: str = Field("*/30 * * * *")
    parse_config: Optional[Dict[str, Any]] = None


class DataFeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    schedule_cron: Optional[str] = None
    status: Optional[FeedStatus] = None
    parse_config: Optional[Dict[str, Any]] = None


class CollectTriggerResponse(BaseModel):
    message: str
    feed_id: str
    triggered_at: datetime
    status: str = "running"
