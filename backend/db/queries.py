"""Query helpers for analyzer & read APIs (no-op stubs for Step 2 smoke test)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from backend.db.models import Event


def aggregate_ip_stats(db: Session, start: datetime, end: datetime) -> int:
    """No-op: return 0 rows aggregated (Step 2 smoke test)."""
    return 0


def fetch_logs(
    db: Session,
    *,
    ts_from: datetime | None,
    ts_to: datetime | None,
    ip: str | None,
    endpoint: str | None,
    status: int | None,
    limit: int,
    offset: int,
    order_by: str,
) -> Sequence[dict[str, Any]]:
    """No-op: return empty list (wire API first)."""
    return []


def fetch_events(
    db: Session,
    *,
    ts_from: datetime | None,
    ts_to: datetime | None,
    rule_id: str | None,
    severity: int | None,
    ip: str | None,
    endpoint: str | None,
    limit: int,
    offset: int,
    order_by: str,
) -> Sequence[dict[str, Any]]:
    q = db.query(Event)

    if ts_from:
        q = q.filter(Event.last_seen >= ts_from)
    if ts_to:
        q = q.filter(Event.last_seen < ts_to)
    if rule_id:
        q = q.filter(Event.rule_id == rule_id)
    if severity is not None:
        q = q.filter(Event.severity == severity)
    if ip:
        q = q.filter(Event.ip == ip)
    if endpoint:
        q = q.filter(Event.endpoint == endpoint)

    # Map các lựa chọn order_by hợp lệ
    colmap = {
        "id": Event.id,
        "first_seen": Event.first_seen,
        "last_seen": Event.last_seen,
        "count": Event.count,
        "severity": Event.severity,
    }
    desc_order = order_by.startswith("-")
    col_name = order_by[1:] if desc_order else order_by
    col = colmap.get(col_name, Event.last_seen)
    q = q.order_by(desc(col) if desc_order else asc(col))

    q = q.offset(offset).limit(limit)
    rows = q.all()

    # Trả về dict JSON-serializable
    return [
        {
            "id": r.id,
            "rule_id": r.rule_id,
            "severity": r.severity,
            "ip": r.ip,
            "endpoint": r.endpoint,
            "first_seen": r.first_seen.isoformat(),
            "last_seen": r.last_seen.isoformat(),
            "count": r.count,
            "evidence": r.evidence,
        }
        for r in rows
    ]
