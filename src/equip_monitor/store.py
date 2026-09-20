"""인메모리 저장소. ponytail: dict 하나. 영속화가 필요해지면 SQLite 로 교체."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from .models import Alarm, Device, Severity, Telemetry


class Store:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.devices: dict[str, Device] = {}
        self.telemetry: dict[str, list[Telemetry]] = defaultdict(list)
        self.alarms: list[Alarm] = []
        self._seq = 0

    # devices
    def upsert_device(self, device: Device) -> Device:
        self.devices[device.id] = device
        return device

    def get_device(self, device_id: str) -> Device | None:
        return self.devices.get(device_id)

    def list_devices(self) -> list[Device]:
        return list(self.devices.values())

    # telemetry
    def add_telemetry(self, t: Telemetry) -> None:
        device = self.devices.get(t.device_id) or self.upsert_device(Device(id=t.device_id, name=t.device_id))
        device.state = t.state
        self.telemetry[t.device_id].append(t)

    def telemetry_for(self, device_id: str, since: datetime | None = None) -> list[Telemetry]:
        return [t for t in self.telemetry.get(device_id, []) if since is None or t.ts >= since]

    # alarms
    def add_alarm(self, device_id: str, rule: str, severity: Severity, message: str, ts: datetime) -> Alarm:
        self._seq += 1
        alarm = Alarm(id=self._seq, device_id=device_id, rule=rule, severity=severity, message=message, ts=ts)
        self.alarms.append(alarm)
        return alarm

    def list_alarms(self, device_id: str | None = None, since: datetime | None = None) -> list[Alarm]:
        return [
            a for a in self.alarms
            if (device_id is None or a.device_id == device_id) and (since is None or a.ts >= since)
        ]

    def ack_alarm(self, alarm_id: int) -> Alarm | None:
        for a in self.alarms:
            if a.id == alarm_id:
                a.acked = True
                return a
        return None


store = Store()
