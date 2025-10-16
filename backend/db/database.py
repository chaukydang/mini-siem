from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import cast

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import settings

# NOTE: DATABASE_URL is Optional in types; validator ensures non-None at runtime.
_db_url: str = cast(str, settings.DATABASE_URL)
_engine: Engine = create_engine(_db_url, future=True, pool_pre_ping=True)

_SessionLocal = sessionmaker(
    bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session: Session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# FastAPI dependency
def get_db() -> Generator[Session, None, None]:
    with session_scope() as s:
        yield s


# For scripts
def get_engine() -> Engine:
    return _engine
