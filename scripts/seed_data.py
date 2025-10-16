from datetime import datetime, timezone

from backend.db.database import session_scope
from backend.db.models import Log

if __name__ == "__main__":
    with session_scope() as s:
        s.add(
            Log(
                ts=datetime.now(timezone.utc),
                source="web",
                host="seed.local",
                ip="127.0.0.1",
                endpoint="/seed",
                method="GET",
                status_code=200,
                resp_time_ms=5,
                ua="seed/1.0",
                action_type="view",
            )
        )
    print("✅ Seeded 1 row.")
