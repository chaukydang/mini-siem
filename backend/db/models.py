from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, Text, UniqueConstraint, text
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

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    # NOT NULL + default để test/seed không cần truyền mọi lúc
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, default="unknown", server_default=text("'unknown'")
    )
    host: Mapped[str] = mapped_column(
        String(255), nullable=False, default="unknown", server_default=text("'unknown'")
    )

    ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    endpoint: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    resp_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    ua: Mapped[Optional[str]] = mapped_column(Text, default=None)
    # FIX chính: có default "http" để tránh NOT NULL bị null
    action_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="http", server_default=text("'http'")
    )

    user_id: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    session_id: Mapped[Optional[str]] = mapped_column(String(128), default=None)
    bytes_in: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    bytes_out: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    referrer: Mapped[Optional[str]] = mapped_column(String(1024), default=None)
    query_params: Mapped[Optional[str]] = mapped_column(Text, default=None)
    error: Mapped[Optional[str]] = mapped_column(Text, default=None)

    raw: Mapped[Optional[str]] = mapped_column(Text, default=None)


# index tổng hợp hữu ích cho truy vấn theo thời gian & IP
Index("ix_logs_ts_ip", Log.ts, Log.ip)


class IngestMetric(Base):
    __tablename__ = "ingest_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts_minute: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    count_ok: Mapped[int] = mapped_column(Integer, nullable=False)
    count_dropped: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_batch_size: Mapped[int] = mapped_column(Integer, nullable=False)
    ingest_latency_p95_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    severity: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    ip: Mapped[Optional[str]] = mapped_column(String(64), index=True, default=None)
    endpoint: Mapped[Optional[str]] = mapped_column(String(1024), default=None)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, default=None)
    source: Mapped[str] = mapped_column(
        String(32), default="rules", server_default=text("'rules'"), nullable=False
    )


Index("ix_events_rule_last", Event.rule_id, Event.last_seen)


class IPStat(Base):
    __tablename__ = "ip_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bucket_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    endpoint: Mapped[Optional[str]] = mapped_column(String(1024), default=None)
    req_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_4xx: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_5xx: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("bucket_start", "ip", "endpoint", name="uq_ip_stats_bucket_ip_ep"),
    )
