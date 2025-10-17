"""Run RuleEngine for a recent window (cron-friendly)."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from backend.db.database import session_scope
from backend.services.anomaly_detector import RuleEngine


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-sec", dest="window_sec", type=int, default=300)
    ap.add_argument("--lookback-minutes", dest="lookback_minutes", type=int, default=15)
    args = ap.parse_args()

    end = datetime.now(timezone.utc)
    start = end - timedelta(seconds=args.window_sec)
    with session_scope() as s:
        written = RuleEngine().process_window(s, start, end)
        print(f"window [{start}..{end}) → events written: {written}")


if __name__ == "__main__":
    main()
