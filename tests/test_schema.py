from backend.services.log_ingestor import LogIngestor

valid_event = {
    "ts": "2025-01-01T00:00:00Z",
    "source": "web",
    "host": "shop.example.com",
    "ip": "203.0.113.10",
    "endpoint": "/login",
    "method": "POST",
    "status_code": 401,
    "resp_time_ms": 42,
    "ua": "Mozilla/5.0",
    "action_type": "login",
}


def test_valid_event_minimal():
    ok, bad = LogIngestor().validate_batch({"events": [valid_event]})
    assert len(ok) == 1
    assert len(bad) == 0


def test_reject_missing_ts():
    e = valid_event.copy()
    e.pop("ts")
    ok, bad = LogIngestor().validate_batch({"events": [e]})
    assert len(ok) == 0
    assert len(bad) == 1
