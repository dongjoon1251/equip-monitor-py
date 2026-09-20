from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from ..models import Alarm, ensure_utc
from ..store import store

router = APIRouter(prefix="/alarms", tags=["alarms"])


@router.get("")
def list_alarms(device_id: str | None = None, since: datetime | None = None) -> list[Alarm]:
    return store.list_alarms(device_id, ensure_utc(since))


@router.post("/{alarm_id}/ack")
def ack_alarm(alarm_id: int) -> Alarm:
    alarm = store.ack_alarm(alarm_id)
    if alarm is None:
        raise HTTPException(404, "alarm not found")
    return alarm
