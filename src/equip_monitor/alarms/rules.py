"""알람 룰. 새 룰은 Rule 프로토콜을 구현하고 DEFAULT_RULES 에 등록한다."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models import Severity, Telemetry


@dataclass(frozen=True)
class Finding:
    severity: Severity
    message: str


class Rule(Protocol):
    name: str

    def evaluate(self, current: Telemetry, history: list[Telemetry]) -> Finding | None:
        """history 는 같은 장비의 이전 텔레메트리(오름차순, current 미포함)."""
        ...


@dataclass
class ThresholdRule:
    """metric 값이 limit 이상이면 즉시 알람."""

    name: str
    metric: str
    limit: float
    severity: Severity = Severity.WARNING

    def evaluate(self, current: Telemetry, history: list[Telemetry]) -> Finding | None:
        value = current.metrics.get(self.metric)
        if value is None or value < self.limit:
            return None
        return Finding(self.severity, f"{self.metric}={value:g} >= {self.limit:g}")


@dataclass
class SustainedThresholdRule:
    """metric 이 limit 이상인 상태가 duration_s 이상 지속되면 1회 알람. 회복 후 재발하면 다시 알람."""

    name: str
    metric: str
    limit: float
    duration_s: float
    severity: Severity = Severity.WARNING

    def _over(self, t: Telemetry) -> bool:
        value = t.metrics.get(self.metric)
        return value is not None and value >= self.limit

    def evaluate(self, current: Telemetry, history: list[Telemetry]) -> Finding | None:
        if not self._over(current):
            return None
        streak = _tail_while(history, self._over)  # 직전까지 이어진 초과 구간 (오름차순)
        start = streak[0].ts if streak else current.ts
        span_now = (current.ts - start).total_seconds()
        span_prev = (streak[-1].ts - start).total_seconds() if streak else 0.0
        if span_now >= self.duration_s and span_prev < self.duration_s:
            return Finding(self.severity, f"{self.metric} >= {self.limit:g} for {span_now / 60:g} min")
        return None


def _tail_while(items: list[Telemetry], pred) -> list[Telemetry]:
    tail: list[Telemetry] = []
    for t in reversed(items):
        if not pred(t):
            break
        tail.append(t)
    return tail[::-1]


DEFAULT_RULES: list[Rule] = [
    ThresholdRule("temp-critical", "temp", 95.0, Severity.CRITICAL),
    ThresholdRule("pressure-high", "pressure", 3.0),
    SustainedThresholdRule("temp-sustained", "temp", 85.0, 300),
]
