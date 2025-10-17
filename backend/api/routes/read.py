from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.queries import fetch_events, fetch_logs

router = APIRouter(prefix="/api", tags=["read"])


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    v = value.strip()
    # Hỗ trợ 'Z' → '+00:00'
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v)


@router.get("/logs")
def get_logs(
    db: Session = Depends(get_db),
    ts_from: Annotated[str | None, Query()] = None,
    ts_to: Annotated[str | None, Query()] = None,
    ip: Annotated[str | None, Query()] = None,
    endpoint: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[str, Query()] = "-ts",
) -> Dict[str, Any]:
    """Return paginated logs. TODO: parse ts_from/ts_to to datetime."""
    rows = fetch_logs(
        db,
        ts_from=None,
        ts_to=None,
        ip=ip,
        endpoint=endpoint,
        status=status,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )
    return {"items": rows, "limit": limit, "offset": offset}


@router.get("/events")
def get_events(
    db: Session = Depends(get_db),
    ts_from: Annotated[str | None, Query()] = None,
    ts_to: Annotated[str | None, Query()] = None,
    rule_id: Annotated[str | None, Query()] = None,
    severity: Annotated[int | None, Query(ge=1, le=5)] = None,
    ip: Annotated[str | None, Query()] = None,
    endpoint: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[str, Query()] = "-last_seen",
) -> Dict[str, Any]:
    items = fetch_events(
        db,
        ts_from=_parse_iso8601(ts_from),
        ts_to=_parse_iso8601(ts_to),
        rule_id=rule_id,
        severity=severity,
        ip=ip,
        endpoint=endpoint,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )
    return {"items": items, "limit": limit, "offset": offset}
