"""가짜 장비 3대. 주기적으로 POST /telemetry 하거나(--scenario), 로그 파일을 POST /ingest 로 재생한다(--replay).

  python simulator/run.py --scenario overheat --interval 1 --count 30
  python simulator/run.py --replay data/samples/overheat.log
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from datetime import datetime, timezone

import httpx

DEVICES = ["DEV-01", "DEV-02", "DEV-03"]


def sample(device: str, tick: int, scenario: str) -> dict:
    temp = 60 + random.uniform(-2, 2)
    if scenario == "overheat" and device == "DEV-02" and tick >= 3:
        temp = min(86 + (tick - 3) * 1.5, 97)  # 86°C 부터 상승, tick 9 부터 95°C 초과
    return {
        "device_id": device,
        "ts": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "temp": round(temp, 1),
            "pressure": round(1.0 + random.uniform(-0.1, 0.1), 2),
            "vibration": round(random.uniform(0, 1), 2),
        },
        "state": "RUN",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", default="http://127.0.0.1:8000")
    p.add_argument("--scenario", choices=["normal", "overheat"], default="normal")
    p.add_argument("--interval", type=float, default=1.0, help="초")
    p.add_argument("--count", type=int, default=60)
    p.add_argument("--replay", metavar="LOG", help="로그 파일을 /ingest 로 한 번에 전송")
    args = p.parse_args()

    with httpx.Client(base_url=args.base, timeout=5) as client:
        if args.replay:
            with open(args.replay, encoding="utf-8") as f:
                r = client.post("/ingest", content=f.read(), headers={"content-type": "text/plain"})
            print(r.status_code, r.json())
            return 0 if r.is_success else 1
        for tick in range(args.count):
            r = client.post("/telemetry", json=[sample(d, tick, args.scenario) for d in DEVICES])
            body = r.json()
            print(f"tick {tick:3d}: accepted={body['accepted']} alarms={[a['rule'] for a in body['alarms']]}")
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
