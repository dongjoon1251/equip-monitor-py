import pytest
from pydantic import ValidationError

from equip_monitor.models import Alarm, DeviceState, Severity, Telemetry
from equip_monitor.store import Store
from helpers import T0, at, tele


def test_telemetry_requires_aware_timestamp():
    with pytest.raises(ValidationError):
        Telemetry(device_id="DEV-01", ts=T0.replace(tzinfo=None), metrics={}, state=DeviceState.RUN)


def test_alarm_requires_aware_timestamp():
    with pytest.raises(ValidationError):
        Alarm(id=1, device_id="DEV-01", rule="r", severity=Severity.WARNING, message="m", ts=T0.replace(tzinfo=None))


def test_add_telemetry_autoregisters_device_and_updates_state():
    s = Store()
    s.add_telemetry(tele("DEV-01", 0, DeviceState.RUN, temp=20.0))
    s.add_telemetry(tele("DEV-01", 1, DeviceState.DOWN, temp=21.0))
    assert s.get_device("DEV-01").state == DeviceState.DOWN
    assert [t.metrics["temp"] for t in s.telemetry_for("DEV-01")] == [20.0, 21.0]
    assert s.telemetry_for("DEV-01", since=at(1))[0].ts == at(1)


def test_alarm_ids_increment_and_ack():
    s = Store()
    a = s.add_alarm("DEV-01", "r", Severity.WARNING, "m", T0)
    b = s.add_alarm("DEV-02", "r", Severity.CRITICAL, "m", at(5))
    assert (a.id, b.id) == (1, 2)
    assert [x.id for x in s.list_alarms(device_id="DEV-02")] == [2]
    assert [x.id for x in s.list_alarms(since=at(5))] == [2]
    assert s.ack_alarm(2).acked is True
    assert s.ack_alarm(99) is None
