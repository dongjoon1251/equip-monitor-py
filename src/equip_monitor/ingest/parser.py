"""raw 로그 라인과 JSON 텔레메트리를 하나의 Telemetry 로 정규화하는 단일 진입점.

라인 포맷: <ISO-8601 UTC ts> <device_id> key=value ...   (state=RUN|IDLE|DOWN|MAINT, 나머지는 숫자)
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from ..models import DeviceState, Telemetry

_LINE = re.compile(r"^(?P<ts>\S+)\s+(?P<device>\S+)\s*(?P<kv>.*)$")
_KV = re.compile(r"(\w+)=(\S+)")
_NUMBER = re.compile(r"^\d+(\.\d+)?$")  # 숫자 토큰


def parse_line(line: str) -> Telemetry:
    m = _LINE.match(line.strip())
    if not m:
        raise ValueError(f"malformed line: {line!r}")
    metrics: dict[str, float] = {}
    state = DeviceState.IDLE
    for key, raw in _KV.findall(m["kv"]):
        if key.lower() == "state":
            state = DeviceState(raw)
        elif _NUMBER.match(raw):
            metrics[key] = float(raw)
        else:
            raise ValueError(f"bad value {key}={raw!r} in {line!r}")
    return normalize(Telemetry(device_id=m["device"], ts=_parse_ts(m["ts"]), metrics=metrics, state=state))


def parse_lines(text: str) -> list[Telemetry]:
    return [parse_line(line) for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def normalize(t: Telemetry) -> Telemetry:
    """JSON·raw 공통: ts 는 UTC 로, metric 키는 소문자로."""
    return t.model_copy(update={
        "ts": t.ts.astimezone(timezone.utc),
        "metrics": {k.lower(): v for k, v in t.metrics.items()},
    })


def _parse_ts(raw: str) -> datetime:
    ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        raise ValueError(f"timestamp must be timezone-aware: {raw!r}")
    return ts
