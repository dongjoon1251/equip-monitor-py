"""텔레메트리 1건을 저장하고 모든 룰로 평가해 Alarm 을 만든다."""
from __future__ import annotations

from ..models import Alarm, Telemetry
from ..store import Store
from ..store import store as default_store
from .rules import DEFAULT_RULES, Rule


class AlarmEngine:
    def __init__(self, store: Store = default_store, rules: list[Rule] | None = None) -> None:
        self.store = store
        self.rules: list[Rule] = list(DEFAULT_RULES if rules is None else rules)

    def process(self, t: Telemetry) -> list[Alarm]:
        history = self.store.telemetry_for(t.device_id)  # current 이전 이력 (복사본)
        self.store.add_telemetry(t)
        raised: list[Alarm] = []
        for rule in self.rules:
            finding = rule.evaluate(t, history)
            if finding is not None:
                raised.append(self.store.add_alarm(t.device_id, rule.name, finding.severity, finding.message, t.ts))
        return raised


engine = AlarmEngine()
