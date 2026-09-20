"""상태별 체류 시간과 가동률. 각 샘플의 상태는 다음 샘플(또는 end)까지 유지된다고 본다."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ..models import DeviceState, Telemetry


def state_durations(telemetry: list[Telemetry], start: datetime, end: datetime) -> dict[str, float]:
    totals = {s.value: 0.0 for s in DeviceState}
    samples = sorted((t for t in telemetry if t.ts < end), key=lambda t: t.ts)
    for i, t in enumerate(samples):
        seg_start = max(t.ts, start)
        seg_end = min(samples[i + 1].ts if i + 1 < len(samples) else end, end)
        if seg_end > seg_start:
            totals[t.state.value] += (seg_end - seg_start).total_seconds()
    return totals


def uptime_ratio(telemetry: list[Telemetry], start: datetime, end: datetime) -> float:
    total = (end - start).total_seconds()
    return state_durations(telemetry, start, end)["RUN"] / total if total > 0 else 0.0


def day_range(day: date) -> tuple[datetime, datetime]:
    """하루 구간 [00:00, 다음날 00:00). 실행 머신의 로컬 시간대 기준."""
    start = datetime.combine(day, time.min).astimezone()
    return start, start + timedelta(days=1)
