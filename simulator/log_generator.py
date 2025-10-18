from __future__ import annotations

import argparse
import random
import string
import time
from datetime import datetime, timezone
from typing import Dict, List

import requests

ENDPOINTS = [
    ("/", "GET"),
    ("/login", "POST"),
    ("/products", "GET"),
    ("/cart/add", "POST"),
    ("/checkout", "POST"),
]
UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/8.0.1",
]
SUS_QS = ["' OR 1=1 --", "UNION SELECT credit_card FROM users", "xp_cmdshell"]


def _rand_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _rand_session() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))


def build_event(
    mode: str, *, attackers: List[str] | None = None, ddos_endpoint: str | None = None
) -> Dict:
    now = datetime.now(timezone.utc).isoformat()
    endpoint, method = random.choice(ENDPOINTS)
    status = 200
    action = "view" if method == "GET" else "action"
    query = None
    # IP mặc định random
    ip = _rand_ip()

    if mode == "brute":
        endpoint, method = "/login", "POST"
        status = random.choice([401, 401, 401, 401, 403, 200])
        action = "login"
        if attackers:
            ip = random.choice(attackers)
    elif mode == "ddos":
        # DDoS: flooding GET (200 là chủ đạo, đôi khi 429)
        if ddos_endpoint:
            endpoint, method = ddos_endpoint, "GET"
        status = random.choice([200, 200, 200, 200, 429])
        action = "view"
        if attackers:
            ip = random.choice(attackers)
    elif mode == "sqli":
        endpoint, method = "/products", "GET"
        status = random.choice([200, 400, 403])
        query = random.choice(SUS_QS)

    return {
        "ts": now,
        "source": "web",
        "host": "shop.example.com",
        "ip": ip,
        "endpoint": endpoint,
        "method": method,
        "status_code": status,
        "resp_time_ms": random.randint(5, 250),
        "ua": random.choice(UAS),
        "action_type": action,
        "session_id": _rand_session(),
        "query_params": query,
    }


def post_batch(url: str, api_key: str, events: List[Dict]):
    r = requests.post(
        url,
        json={"events": events},
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    try:
        print("→", r.status_code, r.json())
    except Exception:
        print("→", r.status_code, r.text[:200])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["normal", "brute", "ddos", "sqli"], default="normal")
    ap.add_argument("--eps", type=int, default=120)
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--batch-size", type=int, default=200)
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--url", default="http://localhost:8000/api/ingest")
    ap.add_argument(
        "--attackers", type=int, default=3, help="Số IP attacker tái sử dụng ở chế độ brute/ddos"
    )
    ap.add_argument(
        "--ddos-endpoint", type=str, default="", help="Cố định endpoint cho ddos (vd: /)"
    )
    args = ap.parse_args()

    deadline = time.time() + args.duration
    buf: List[Dict] = []
    interval = 1.0 / max(1, args.eps)

    # Chuẩn bị pool attackers cho brute
    attackers_pool: List[str] = []
    if args.mode in ("brute", "ddos"):
        attackers_pool = [_rand_ip() for _ in range(max(1, args.attackers))]
    while time.time() < deadline:
        ev = build_event(
            args.mode if random.random() < 0.9 else "normal",
            attackers=attackers_pool if args.mode in ("brute", "ddos") else None,
            ddos_endpoint=args.ddos_endpoint or None,
        )
        buf.append(ev)
        if len(buf) >= args.batch_size:
            post_batch(args.url, args.api_key, buf)
            buf = []
        time.sleep(interval)

    if buf:
        post_batch(args.url, args.api_key, buf)


if __name__ == "__main__":
    main()
