from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from ..models import Device, Telemetry, ensure_utc
from ..store import store

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", status_code=201)
def upsert_device(device: Device) -> Device:
    return store.upsert_device(device)


@router.get("")
def list_devices() -> list[Device]:
    return store.list_devices()


@router.get("/{device_id}")
def get_device(device_id: str) -> Device:
    device = store.get_device(device_id)
    if device is None:
        raise HTTPException(404, "device not found")
    return device


@router.get("/{device_id}/telemetry")
def device_telemetry(device_id: str, since: datetime | None = None) -> list[Telemetry]:
    return store.telemetry_for(device_id, ensure_utc(since))
