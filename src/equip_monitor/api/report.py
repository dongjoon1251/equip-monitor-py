from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from ..report.uptime import day_range, state_durations, uptime_ratio
from ..store import store

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/uptime")
def uptime_report(
    from_: date = Query(alias="from"),
    to: date = Query(...),
    device_id: str | None = None,
) -> list[dict]:
    """[from, to] 날짜(양 끝 포함) 구간의 장비별 상태 체류시간과 가동률."""
    start, _ = day_range(from_)
    _, end = day_range(to)
    if device_id is not None:
        device = store.get_device(device_id)
        if device is None:
            raise HTTPException(404, "device not found")
        devices = [device]
    else:
        devices = store.list_devices()
    rows = []
    for d in devices:
        telemetry = store.telemetry_for(d.id)
        rows.append({
            "device_id": d.id,
            "from": start,
            "to": end,
            "durations_s": state_durations(telemetry, start, end),
            "uptime_ratio": round(uptime_ratio(telemetry, start, end), 4),
        })
    return rows
