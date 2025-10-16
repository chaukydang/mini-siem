from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.db.models import IngestMetric, Log


# Pydantic schema for strict validation
class LogEvent(BaseModel):
    ts: datetime
    source: str
    host: str
    ip: str
    endpoint: str
    method: str
    status_code: int
    resp_time_ms: int
    ua: str
    action_type: str

    user_id: str | None = None
    session_id: str | None = None
    bytes_in: int | None = None
    bytes_out: int | None = None
    referrer: str | None = None
    query_params: str | None = None
    error: str | None = None
    raw: str | None = None


class IngestPayload(BaseModel):
    events: List[LogEvent] = Field(default_factory=list)


class LogIngestor:
    def validate_batch(
        self, payload: Dict[str, Any]
    ) -> Tuple[List[LogEvent], List[Dict[str, Any]]]:
        """Validate incoming payload. Return (accepted_models, rejected_raw)."""
        rejected: List[Dict[str, Any]] = []
        try:
            model = IngestPayload.model_validate(payload)
        except Exception:
            # payload shape is wrong
            return [], [payload]

        accepted: List[LogEvent] = []
        for e in model.events:
            try:
                # normalize timezone to UTC if naive
                if e.ts.tzinfo is None:
                    e.ts = e.ts.replace(tzinfo=timezone.utc)
                accepted.append(e)
            except Exception:
                rejected.append(e.model_dump())
        return accepted, rejected

    def save_batch(self, db: Session, rows: List[LogEvent]) -> int:
        """Persist validated events into DB. Returns number inserted."""
        if not rows:
            return 0
        db.add_all(
            [
                Log(
                    ts=e.ts,
                    source=e.source,
                    host=e.host,
                    ip=e.ip,
                    endpoint=e.endpoint,
                    method=e.method,
                    status_code=e.status_code,
                    resp_time_ms=e.resp_time_ms,
                    ua=e.ua,
                    action_type=e.action_type,
                    user_id=e.user_id,
                    session_id=e.session_id,
                    bytes_in=e.bytes_in,
                    bytes_out=e.bytes_out,
                    referrer=e.referrer,
                    query_params=e.query_params,
                    error=e.error,
                    raw=e.raw,
                )
                for e in rows
            ]
        )
        return len(rows)

    def update_metrics(
        self, db: Session, accepted: int, dropped: int, p95_ms: int, batch_size: int
    ) -> None:
        now_minute = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        db.add(
            IngestMetric(
                ts_minute=now_minute,
                count_ok=accepted,
                count_dropped=dropped,
                avg_batch_size=batch_size,
                ingest_latency_p95_ms=p95_ms,
            )
        )
