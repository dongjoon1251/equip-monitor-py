from equip_monitor.alarms.engine import AlarmEngine
from equip_monitor.alarms.rules import DEFAULT_RULES, SustainedThresholdRule
from equip_monitor.models import Severity
from equip_monitor.store import Store
from helpers import tele


def sustained() -> AlarmEngine:
    return AlarmEngine(Store(), [SustainedThresholdRule("temp-sustained", "temp", 85.0, 300)])


def feed(engine: AlarmEngine, minutes_and_temps: list[tuple[float, float]]) -> list[float]:
    """알람이 발생한 분(minute) 목록."""
    fired = []
    for m, temp in minutes_and_temps:
        if engine.process(tele(minutes=m, temp=temp)):
            fired.append(m)
    return fired


def test_fires_once_when_duration_reached_exactly():
    fired = feed(sustained(), [(0, 86), (1, 86), (2, 86), (3, 86), (4, 86), (5, 86), (6, 86)])
    assert fired == [5]


def test_does_not_fire_below_duration():
    assert feed(sustained(), [(0, 86), (4 + 59 / 60, 86)]) == []


def test_below_limit_resets_streak():
    assert feed(sustained(), [(0, 86), (2, 84.9), (3, 86), (7, 86)]) == []
    assert feed(sustained(), [(0, 86), (2, 84.9), (3, 86), (8, 86)]) == [8]


def test_realarm_after_recovery():
    seq = [(0, 86), (5, 86), (6, 70), (7, 86), (12, 86)]
    assert feed(sustained(), seq) == [5, 12]


def test_alarm_content():
    engine = sustained()
    engine.process(tele(minutes=0, temp=90))
    alarm = engine.process(tele(minutes=5, temp=90))[0]
    assert alarm.severity == Severity.WARNING
    assert alarm.message == "temp >= 85 for 5 min"


def test_default_rules_include_sustained():
    assert [r.name for r in DEFAULT_RULES] == ["temp-critical", "pressure-high", "temp-sustained"]
