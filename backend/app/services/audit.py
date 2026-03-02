"""Audit logging service (Constitution Principle IV).

Records sensitive write operations: case CRUD, feed CRUD, auth login.
Stored in-memory log for MVP; production should persist to DB or external log sink.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger("audit")


def log_action(actor: str, action: str, target_type: str, target_id: str) -> None:
    """Write a structured audit log entry. MUST NOT include passwords or secrets."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
    }
    logger.info("AUDIT %s", entry)
