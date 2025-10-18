from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from backend.db.database import get_engine
from backend.db.models import Base


@pytest.fixture(autouse=True)
def _setup_db() -> Iterator[None]:
    """Ensure tables exist; truncate between tests."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    # best-effort truncate (some tables may not exist in early steps)
    with engine.begin() as conn:
        for tbl in ("events", "ip_stats", "logs"):
            try:
                conn.exec_driver_sql(f'TRUNCATE TABLE "{tbl}" RESTART IDENTITY CASCADE;')
            except Exception:
                pass


@pytest.fixture()
def db() -> Iterator[Session]:
    """Yield a short-lived session for each test."""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as s:
        yield s
