from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException

from ..alarms.engine import engine
from ..ingest.parser import normalize, parse_lines
from ..models import Alarm, Telemetry

router = APIRouter(tags=["telemetry"])


def _process(items: list[Telemetry]) -> dict:
    alarms: list[Alarm] = [a for t in items for a in engine.process(t)]
    return {"accepted": len(items), "alarms": alarms}


@router.post("/telemetry", status_code=202)
def post_telemetry(items: list[Telemetry]) -> dict:
    """JSON 텔레메트리 배치."""
    return _process([normalize(t) for t in items])


@router.post("/ingest", status_code=202)
def post_ingest(body: str = Body(..., media_type="text/plain")) -> dict:
    """raw 로그 라인 배치 (시뮬레이터 --replay, 장비 게이트웨이)."""
    try:
        items = parse_lines(body)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    return _process(items)
