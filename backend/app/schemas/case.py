"""Case and Tag Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.case import CaseStatus


class TagOut(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class TagWithCount(TagOut):
    case_count: int = 0


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class CaseSummary(BaseModel):
    id: str
    title: str
    status: CaseStatus
    hotness_score: float
    tags: List[TagOut] = []
    event_count: int = 0
    source_count: int = 0
    created_at: datetime
    last_event_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CaseDetail(CaseSummary):
    description: Optional[str] = None


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    tag_ids: List[str] = []


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    tag_ids: Optional[List[str]] = None


class SearchSuggestedCase(BaseModel):
    id: str
    title: str
    status: CaseStatus
    event_count: int = 0
