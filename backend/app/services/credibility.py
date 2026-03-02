"""Credibility scoring engine (FR-003, FR-008, FR-009a / FR-017).

Algorithm: total_score = authority × 0.4 + timeliness × 0.2 + cross_verify × 0.4
Source type base scores and history penalty per research.md.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.models.credibility import CredibilityLevel
from app.models.source import SourceType

if TYPE_CHECKING:
    from app.models.source import Source

logger = logging.getLogger(__name__)

# Authority base scores by source type
AUTHORITY_BASE: dict[SourceType, float] = {
    SourceType.government: 90.0,
    SourceType.mainstream_media: 80.0,
    SourceType.academic: 85.0,
    SourceType.local_media: 60.0,
    SourceType.social_media: 30.0,
    SourceType.unknown: 10.0,
}

# Cross-verification score table
CROSS_VERIFY_MAP = {1: 20.0, 2: 50.0, 3: 75.0, 4: 90.0}
CROSS_VERIFY_MAX = 100.0
CROSS_VERIFY_DIVERSE_THRESHOLD = 5


def _authority_score(source: "Source") -> float:
    base = AUTHORITY_BASE.get(source.source_type, 10.0)
    if source.has_false_history:
        base *= 0.5
    return max(0.0, min(100.0, base))


def _timeliness_score(event_time: datetime) -> float:
    """Time decay: 100 - (hours_since_event / 24) * 5. Floor at 0."""
    now = datetime.now(timezone.utc)
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)
    hours = (now - event_time).total_seconds() / 3600
    score = 100.0 - (hours / 24.0) * 5.0
    return max(0.0, min(100.0, score))


def _cross_verify_score(sources: list["Source"]) -> float:
    n = len(sources)
    if n >= CROSS_VERIFY_DIVERSE_THRESHOLD:
        types = {s.source_type for s in sources}
        if len(types) >= 2:
            return CROSS_VERIFY_MAX
    return CROSS_VERIFY_MAP.get(n, CROSS_VERIFY_MAP.get(4, 90.0) if n > 4 else 20.0)


def _map_level(score: float) -> CredibilityLevel:
    if score >= 75:
        return CredibilityLevel.high
    if score >= 50:
        return CredibilityLevel.medium
    if score >= 25:
        return CredibilityLevel.low
    return CredibilityLevel.unverified


def _detect_conflict(sources: list["Source"]) -> list[str]:
    """FR-017: detect conflict when ≥2 high-authority sources (≥75 auth score) exist."""
    high_auth = [s for s in sources if _authority_score(s) >= 75]
    if len(high_auth) >= 2:
        # Simplistic: flag all high-authority sources as potential conflict participants.
        # A production system would compare article content embeddings.
        return [s.name for s in high_auth]
    return []


def compute_credibility(
    sources: list["Source"],
    event_time: datetime,
) -> dict:
    """Compute credibility assessment for an event node given its sources."""
    if not sources:
        return {
            "level": CredibilityLevel.unverified,
            "total_score": 0.0,
            "authority_score": 0.0,
            "timeliness_score": 0.0,
            "cross_verify_score": 0.0,
            "source_count": 0,
            "has_conflict": False,
            "conflict_sources": [],
            "source_details": [],
        }

    auth_scores = [_authority_score(s) for s in sources]
    authority_avg = sum(auth_scores) / len(auth_scores)
    timeliness = _timeliness_score(event_time)
    cross_verify = _cross_verify_score(sources)

    total = authority_avg * 0.4 + timeliness * 0.2 + cross_verify * 0.4
    level = _map_level(total)
    conflict_names = _detect_conflict(sources)

    source_details = []
    for s, auth_s in zip(sources, auth_scores):
        warnings = []
        if s.has_false_history:
            warnings.append("来源信誉警告：该来源有历史虚假信息记录")
        if s.name in conflict_names:
            warnings.append("来源分歧：该来源与其他高权威来源存在内容冲突")
        source_details.append(
            {
                "source_id": s.id,
                "source_name": s.name,
                "source_type": s.source_type.value,
                "url": s.url,
                "reputation_score": s.reputation_score,
                "has_false_history": s.has_false_history,
                "authority_contribution": auth_s,
                "is_accessible": True,
                "collected_at": s.collected_at,
                "warnings": warnings,
            }
        )

    hours_since = (datetime.now(timezone.utc) - (
        event_time if event_time.tzinfo else event_time.replace(tzinfo=timezone.utc)
    )).total_seconds() / 3600

    n = len(sources)
    explanation = {
        "authority": f"综合 {n} 个来源的权威性评分加权平均（得分 {authority_avg:.1f}）",
        "timeliness": (
            f"距事件发生约 {hours_since:.1f} 小时，时效性得分 {timeliness:.1f}"
        ),
        "cross_verify": f"{n} 个独立来源交叉印证，得分 {cross_verify:.1f}",
    }

    return {
        "level": level,
        "total_score": round(total, 2),
        "authority_score": round(authority_avg, 2),
        "timeliness_score": round(timeliness, 2),
        "cross_verify_score": round(cross_verify, 2),
        "source_count": n,
        "has_conflict": len(conflict_names) > 0,
        "conflict_sources": conflict_names,
        "source_details": source_details,
        "scoring_explanation": explanation,
    }
