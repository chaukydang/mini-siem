from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.db.models import Log
from backend.main import app
from backend.services.anomaly_detector import RuleEngine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def test_api_events_r003(db: Session) -> None:
    client = TestClient(app)

    now = _utcnow()
    ip = "192.0.2.55"

    # Seed a few SQLi-like logs
    for p in ("' OR 1=1 --", "SLEEP(1)", "UNION SELECT id FROM users"):
        db.add(
            Log(
                ts=now - timedelta(seconds=5),
                source="pytest",
                host="pytest-host",
                ip=ip,
                method="GET",
                endpoint="/search",
                status_code=200,
                resp_time_ms=9,
                bytes_out=128,
                query_params=p,
            )
        )
    db.commit()

    # Run analyzer for last 5 minutes
    start = now - timedelta(seconds=300)
    end = now
    RuleEngine().process_window(db, start, end)
    db.commit()

    # Call API
    resp = client.get("/api/events", params={"rule_id": "R-003", "limit": 5})
    assert resp.status_code == 200
    data: dict[str, Any] = resp.json()
    items = data.get("items", [])
    assert isinstance(items, list) and len(items) >= 1
    assert items[0]["rule_id"] == "R-003"
