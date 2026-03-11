"""EventNode Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.credibility import CredibilityLevel


class CredibilityBrief(BaseModel):
    level: CredibilityLevel
    total_score: float
    has_conflict: bool = False


class SourceBrief(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    reputation_score: float
    has_false_history: bool
    collected_at: datetime

    model_config = {"from_attributes": True}


class EventSummary(BaseModel):
    id: str
    title: str
    event_time: datetime
    source_count: int = 0
    credibility: Optional[CredibilityBrief] = None
    sources: List[SourceBrief] = []

    model_config = {"from_attributes": True}


class EventDetail(EventSummary):
    case_id: str
    summary: Optional[str] = None
    sources: List[SourceBrief] = []
