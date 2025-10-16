from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Common Schema required & optional keys (for reference)
COMMON_SCHEMA_REQUIRED = [
    "ts",
    "source",
    "host",
    "ip",
    "endpoint",
    "method",
    "status_code",
    "resp_time_ms",
    "ua",
    "action_type",
]
COMMON_SCHEMA_OPTIONAL = [
    "user_id",
    "session_id",
    "bytes_in",
    "bytes_out",
    "referrer",
    "query_params",
    "error",
]


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(32))
    host: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(64), index=True)

    endpoint: Mapped[str] = mapped_column(String(1024), index=True)
    method: Mapped[str] = mapped_column(String(16))
    status_code: Mapped[int] = mapped_column(Integer)
    resp_time_ms: Mapped[int] = mapped_column(Integer)

    ua: Mapped[Optional[str]] = mapped_column(Text, default=None)
    action_type: Mapped[str] = mapped_column(String(64))

    user_id: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    session_id: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    bytes_in: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    bytes_out: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    referrer: Mapped[Optional[str]] = mapped_column(String(1024), default=None)
    query_params: Mapped[Optional[str]] = mapped_column(Text, default=None)
    error: Mapped[Optional[str]] = mapped_column(Text, default=None)

    raw: Mapped[Optional[str]] = mapped_column(Text, default=None)


Index("ix_logs_ts_ip", Log.ts, Log.ip)


class IngestMetric(Base):
    __tablename__ = "ingest_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts_minute: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    count_ok: Mapped[int] = mapped_column(Integer)
    count_dropped: Mapped[int] = mapped_column(Integer)
    avg_batch_size: Mapped[int] = mapped_column(Integer)
    ingest_latency_p95_ms: Mapped[int] = mapped_column(Integer)
