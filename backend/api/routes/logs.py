from __future__ import annotations

import time
from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.database import get_db
from backend.services.log_ingestor import LogIngestor

router = APIRouter(prefix="/api", tags=["logs"])


def _check_api_key(api_key: str | None) -> None:
    allowed = {k.strip() for k in settings.API_KEYS.split(",") if k.strip()}
    if not api_key or api_key not in allowed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.post("/ingest")
def ingest_batch(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> Dict[str, int]:
    _check_api_key(x_api_key)

    svc = LogIngestor()
    t0 = time.perf_counter_ns()
    accepted_models, rejected = svc.validate_batch(payload)
    inserted = svc.save_batch(db, accepted_models)
    p95_ms = int((time.perf_counter_ns() - t0) / 1_000_000)
    svc.update_metrics(db, inserted, len(rejected), p95_ms=p95_ms, batch_size=len(accepted_models))

    return {
        "accepted": inserted,
        "dropped": len(rejected),
        "latency_ms": p95_ms,
    }


@router.get("/health")
def health(db: Session = Depends(get_db)) -> Dict[str, bool | str]:
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        return {"status": "degraded", "db": False, "error": str(e)}
    return {"status": "ok", "db": db_ok}
