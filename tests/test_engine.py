from equip_monitor.alarms.engine import AlarmEngine
from equip_monitor.alarms.rules import DEFAULT_RULES, Finding, ThresholdRule
from equip_monitor.models import Severity
from equip_monitor.store import Store
from helpers import tele


def test_threshold_rule_fires_at_limit_not_below():
    engine = AlarmEngine(Store(), [ThresholdRule("temp-critical", "temp", 95.0, Severity.CRITICAL)])
    assert engine.process(tele(minutes=0, temp=94.9)) == []
    alarms = engine.process(tele(minutes=1, temp=95.0))
    assert [(a.rule, a.severity) for a in alarms] == [("temp-critical", Severity.CRITICAL)]
    assert alarms[0].ts == tele(minutes=1).ts


def test_missing_metric_is_ignored():
    engine = AlarmEngine(Store(), [ThresholdRule("pressure-high", "pressure", 3.0)])
    assert engine.process(tele(temp=99.0)) == []


def test_engine_gives_rule_prior_history_only():
    seen: list[int] = []

    class Spy:
        name = "spy"

        def evaluate(self, current, history):
            seen.append(len(history))
            return None

    engine = AlarmEngine(Store(), [Spy()])
    for m in range(3):
        engine.process(tele(minutes=m, temp=1.0))
    assert seen == [0, 1, 2]


def test_alarm_is_persisted_in_store():
    s = Store()
    AlarmEngine(s, [ThresholdRule("r", "temp", 1.0)]).process(tele(temp=2.0))
    assert s.list_alarms()[0].message == "temp=2 >= 1"


def test_default_rules_are_threshold_rules():
    assert [r.name for r in DEFAULT_RULES] == ["temp-critical", "pressure-high"]
    assert isinstance(Finding(Severity.INFO, "x"), Finding)
