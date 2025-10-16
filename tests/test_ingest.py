import os

from fastapi.testclient import TestClient

from backend.main import app

os.environ.setdefault("API_KEYS", "dev-key-1,dev-key-2")
client = TestClient(app)


payload = {
    "events": [
        {
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
    ]
}


def test_ingest_happy_path():
    r = client.post("/api/ingest", json=payload, headers={"X-API-Key": "dev-key-1"})
    assert r.status_code == 200
    j = r.json()
    assert j["accepted"] == 1


def test_ingest_auth_failure():
    r = client.post("/api/ingest", json=payload)
    assert r.status_code == 401
