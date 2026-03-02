"""Credibility Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.credibility import CredibilityLevel


class ScoringExplanation(BaseModel):
    authority: str
    timeliness: str
    cross_verify: str


class SourceWithCredibility(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    url: str
    reputation_score: float
    has_false_history: bool
    authority_contribution: float
    is_accessible: bool = True
    collected_at: datetime
    warnings: List[str] = []


class CredibilityDetail(BaseModel):
    event_id: str
    event_title: str
    level: CredibilityLevel
    total_score: float
    authority_score: float
    timeliness_score: float
    cross_verify_score: float
    source_count: int
    has_conflict: bool = False
    conflict_sources: List[str] = []
    sources: List[SourceWithCredibility] = []
    scoring_explanation: Optional[ScoringExplanation] = None
    assessed_at: datetime


class CredibilityOverall(BaseModel):
    """Top-level response for GET /events/{id}/credibility."""
    event_id: str
    level: CredibilityLevel
    total_score: float
    has_conflict: bool = False
    conflict_sources: List[str] = []
    detail: CredibilityDetail
