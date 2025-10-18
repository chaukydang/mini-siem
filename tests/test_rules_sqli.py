from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.db.models import Event, Log
from backend.services.anomaly_detector import RuleEngine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def test_r003_sqli_generates_event(db: Session) -> None:
    """Seed ≥ min_hits SQLi-like requests from the same IP → expect 1+ events R-003."""
    now = _utcnow()
    ip = "198.51.100.77"

    # Seed 4 logs with SQLi signatures within the window and allowed endpoint (/search)
    payloads = [
        "' OR 1=1 --",
        "UNION SELECT username, password FROM users",
        "SLEEP(2)",
        "benchmark(1000000,md5(1))",
    ]
    for p in payloads:
        db.add(
            Log(
                ts=now - timedelta(seconds=10),
                source="pytest",
                host="pytest-host",
                ip=ip,
                method="GET",
                endpoint="/search",
                status_code=200,
                resp_time_ms=10,
                bytes_out=512,
                query_params=p,
            )
        )
    db.commit()

    # Analyze 5-minute window containing those logs
    start = now - timedelta(seconds=300)
    end = now
    written = RuleEngine().process_window(db, start, end)
    db.commit()

    assert written >= 1

    events = (
        db.query(Event)
        .filter(Event.rule_id == "R-003", Event.ip == ip)
        .order_by(Event.id.desc())
        .all()
    )
    assert events, "Expected at least one R-003 event"
    assert events[0].count >= 3  # min_hits_per_ip default in rules.yaml


def test_r003_endpoint_whitelist(db: Session) -> None:
    """
    If rules.yaml whitelists endpoints (e.g. /search, /product),
    SQLi-like hits on other endpoints alone should not trigger.
    """
    now = _utcnow()
    ip = "203.0.113.45"

    # 3 hits on /login (not whitelisted in the example), should not count alone
    for _ in range(3):
        db.add(
            Log(
                ts=now - timedelta(seconds=20),
                source="pytest",
                host="pytest-host",
                ip=ip,
                method="GET",
                endpoint="/login",
                status_code=200,
                resp_time_ms=12,
                bytes_out=256,
                query_params="' OR 1=1 --",
            )
        )
    # 3 hits on /search (whitelisted) — should trigger
    for _ in range(3):
        db.add(
            Log(
                ts=now - timedelta(seconds=15),
                source="pytest",
                host="pytest-host",
                ip=ip,
                method="GET",
                endpoint="/search",
                status_code=200,
                resp_time_ms=11,
                bytes_out=256,
                query_params="UNION SELECT credit_card FROM payments",
            )
        )
    db.commit()

    start = now - timedelta(seconds=300)
    end = now
    written = RuleEngine().process_window(db, start, end)
    db.commit()
    assert written >= 1

    # Verify there is at least one R-003 event for that IP
    assert db.query(Event).filter(Event.rule_id == "R-003", Event.ip == ip).count() >= 1
