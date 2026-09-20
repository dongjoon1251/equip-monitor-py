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


DEFAULT_RULES: list[Rule] = [
    ThresholdRule("temp-critical", "temp", 95.0, Severity.CRITICAL),
    ThresholdRule("pressure-high", "pressure", 3.0),
]
