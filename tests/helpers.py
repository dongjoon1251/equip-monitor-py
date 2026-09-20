from datetime import datetime, timedelta, timezone

from equip_monitor.models import DeviceState, Telemetry

T0 = datetime(2026, 9, 21, 9, 0, tzinfo=timezone.utc)


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def tele(device_id: str = "DEV-01", minutes: float = 0.0, state: DeviceState = DeviceState.RUN, **metrics: float) -> Telemetry:
    return Telemetry(device_id=device_id, ts=at(minutes), metrics=metrics, state=state)
