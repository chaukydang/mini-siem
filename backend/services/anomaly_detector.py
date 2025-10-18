"""Rule Engine — evaluates logs over a sliding window and writes events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.rules_config import rules_config
from backend.db.models import Event, Log
from backend.db.queries import aggregate_ip_stats


@dataclass
class RuleMatch:
    rule_id: str
    severity: int
    first_seen: datetime
    last_seen: datetime
    ip: str | None = None
    endpoint: str | None = None
    count: int = 0
    evidence: str | None = None


class Rule(Protocol):
    rule_id: str

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]: ...


class BruteForceRule:
    rule_id = "R-001"

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]:
        """Đếm số lần login thất bại (401/403) tới endpoint cấu hình theo IP trong window."""
        cfg = rules_config.get(self.rule_id) or {}
        min_failures = int(cfg.get("min_failures", 8))
        login_endpoint = cfg.get("login_endpoint", "/login")
        severity = int(cfg.get("severity", 4))

        # SELECT ip, MIN(ts) AS first_seen, MAX(ts) AS last_seen, COUNT(*) AS cnt
        # FROM logs
        # WHERE ts >= start AND ts < end
        #   AND endpoint = login_endpoint
        #   AND status_code IN (401,403)
        # GROUP BY ip
        # HAVING COUNT(*) >= min_failures

        q = (
            db.query(
                Log.ip.label("ip"),
                func.min(Log.ts).label("first_seen"),
                func.max(Log.ts).label("last_seen"),
                func.count(Log.id).label("cnt"),
            )
            .filter(
                Log.ts >= start,
                Log.ts < end,
                Log.endpoint == login_endpoint,
                Log.status_code.in_([401, 403]),
            )
            .group_by(Log.ip)
            .having(func.count(Log.id) >= min_failures)
        )

        matches: list[RuleMatch] = []
        for row in q.all():
            ip = row.ip
            first_seen = row.first_seen
            last_seen = row.last_seen
            cnt = int(row.cnt)
            evidence = (
                f"{cnt} failed logins to {login_endpoint} within {(end-start).total_seconds():.0f}s"
            )
            matches.append(
                RuleMatch(
                    rule_id=self.rule_id,
                    severity=severity,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    ip=ip,
                    endpoint=login_endpoint,
                    count=cnt,
                    evidence=evidence,
                )
            )
        return matches


class SQLiSignatureRule:
    rule_id = "R-003"

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]:
        # TODO: Step 2.3
        return []


class Http5xxSpikeRule:
    rule_id = "R-004"

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]:
        # TODO: Step 2.4
        return []


class AdminProbingRule:
    rule_id = "R-005"

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]:
        # TODO: Step 2.5
        return []


class RuleEngine:
    """Coordinates windowing, aggregation, rule evaluation, and event writes."""

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = rules or [
            BruteForceRule(),
            DDOSLightRule(),
            SQLiSignatureRule(),
            Http5xxSpikeRule(),
            AdminProbingRule(),
        ]
        rules_config.load()

    def process_window(self, db: Session, start: datetime, end: datetime) -> int:
        # 1) (Optional) rollup — để 0 trong Step 2 tối thiểu
        aggregate_ip_stats(db, start, end)

        # 2) evaluate rules
        matches: list[RuleMatch] = []
        for r in self.rules:
            matches.extend(r.evaluate(db, start, end))

        # 3) persist events (MVP: insert mới; Step 4 sẽ merge/idempotent)
        written = 0
        for m in matches:
            db.add(
                Event(
                    rule_id=m.rule_id,
                    severity=m.severity,
                    ip=m.ip,
                    endpoint=m.endpoint,
                    first_seen=m.first_seen,
                    last_seen=m.last_seen,
                    count=m.count,
                    evidence=m.evidence,
                    source="rules",
                )
            )
            written += 1
        return written


class DDOSLightRule:
    rule_id = "R-002"

    def evaluate(self, db: Session, start: datetime, end: datetime) -> list[RuleMatch]:
        """Phát hiện IP có số lượng request vượt ngưỡng trong cửa sổ [start, end)."""
        cfg = rules_config.get(self.rule_id) or {}
        threshold = int(cfg.get("req_per_ip_threshold", 400))
        focus_endpoint = cfg.get("endpoint")  # có thể None
        severity = int(cfg.get("severity", 4))

        q = db.query(
            Log.ip.label("ip"),
            func.min(Log.ts).label("first_seen"),
            func.max(Log.ts).label("last_seen"),
            func.count(Log.id).label("cnt"),
        ).filter(Log.ts >= start, Log.ts < end)
        if focus_endpoint:
            q = q.filter(Log.endpoint == focus_endpoint)

        q = q.group_by(Log.ip).having(func.count(Log.id) >= threshold)

        matches: list[RuleMatch] = []
        for row in q.all():
            ip = row.ip
            first_seen = row.first_seen
            last_seen = row.last_seen
            cnt = int(row.cnt)
            ep = focus_endpoint or "<any>"
            evidence = f"{cnt} requests in {(end-start).total_seconds():.0f}s to {ep}"
            matches.append(
                RuleMatch(
                    rule_id=self.rule_id,
                    severity=severity,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    ip=ip,
                    endpoint=focus_endpoint,  # None nếu theo dõi all
                    count=cnt,
                    evidence=evidence,
                )
            )
        return matches
