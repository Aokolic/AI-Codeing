"""NLP semantic matcher for automatic event deduplication (FR-002a).

Uses shibing624/text2vec-base-chinese with cosine similarity threshold 0.82
and ±48h time window to match new articles to existing event nodes.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import numpy as np
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

if TYPE_CHECKING:
    from app.models.event_node import EventNode

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level model cache (loaded once on first use)
_model = None


def _get_model():
    """Load the sentence-transformer model lazily (≈400 MB, cached after first load)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading NLP model: %s", settings.nlp_model_name)
            _model = SentenceTransformer(settings.nlp_model_name)
            logger.info("NLP model loaded successfully.")
        except Exception as exc:
            logger.warning("Failed to load NLP model (%s). Dedup disabled.", exc)
            _model = None
    return _model


def encode_text(text: str) -> list[float] | None:
    """Encode text to 768-dim embedding. Returns None if model unavailable."""
    model = _get_model()
    if model is None:
        return None
    try:
        vec = model.encode(text, normalize_embeddings=True)
        return vec.tolist()
    except Exception as exc:
        logger.warning("Encoding failed: %s", exc)
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


async def find_matching_event(
    db: AsyncSession,
    case_id: str,
    title: str,
    summary: str,
    event_time: datetime,
) -> "EventNode | None":
    """Find an existing EventNode that matches the given article within ±48h window.

    Returns the best-matching EventNode above the similarity threshold, or None.
    """
    from app.models.event_node import EventNode

    text = f"{title} {summary}"
    embedding = encode_text(text)
    if embedding is None:
        # NLP unavailable — skip dedup, always create new node
        return None

    window = timedelta(hours=settings.nlp_time_window_hours)
    time_lower = event_time - window
    time_upper = event_time + window

    # Fetch candidates in the time window for this case
    stmt = select(EventNode).where(
        and_(
            EventNode.case_id == case_id,
            EventNode.event_time >= time_lower,
            EventNode.event_time <= time_upper,
            EventNode.embedding_json.is_not(None),
        )
    )
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    best_node: EventNode | None = None
    best_score = 0.0

    for node in candidates:
        try:
            node_embedding = json.loads(node.embedding_json)  # type: ignore[arg-type]
        except (json.JSONDecodeError, TypeError):
            continue
        score = cosine_similarity(embedding, node_embedding)
        if score >= settings.nlp_similarity_threshold and score > best_score:
            best_score = score
            best_node = node

    if best_node:
        logger.debug(
            "Matched article '%s' → EventNode %s (score=%.3f)",
            title,
            best_node.id,
            best_score,
        )
    return best_node
