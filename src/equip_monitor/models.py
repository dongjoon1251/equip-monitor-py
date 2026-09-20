"""도메인 모델. 모든 datetime 은 timezone-aware UTC."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class DeviceState(str, Enum):
    RUN = "RUN"
    IDLE = "IDLE"
    DOWN = "DOWN"
    MAINT = "MAINT"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Device(BaseModel):
    id: str
    name: str = ""
    type: str = "generic"
    location: str = ""
    state: DeviceState = DeviceState.IDLE


class Telemetry(BaseModel):
    device_id: str
    ts: datetime
    metrics: dict[str, float] = Field(default_factory=dict)
    state: DeviceState = DeviceState.IDLE

    @field_validator("ts")
    @classmethod
    def _must_be_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("ts must be timezone-aware (UTC)")
        return v


class Alarm(BaseModel):
    id: int
    device_id: str
    rule: str
    severity: Severity
    message: str
    ts: datetime
    acked: bool = False


def ensure_utc(dt: datetime | None) -> datetime | None:
    """쿼리 파라미터용: naive 는 UTC 로 간주하고, aware 는 UTC 로 변환."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
