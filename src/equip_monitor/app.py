"""FastAPI 앱 조립. 실행: uvicorn equip_monitor.app:app --reload"""
from __future__ import annotations

import os
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import alarms, devices, report, telemetry


def create_app() -> FastAPI:
    app = FastAPI(title="equip-monitor", version="0.1.0")
    api_key = os.environ.get("EQUIP_API_KEY")

    if api_key:
        # ponytail: 조회(GET)만 키 검사 — 게이트웨이/시뮬레이터 수집(POST)은 그대로. 수집도 막아야 하면 method 조건 제거
        @app.middleware("http")
        async def require_api_key(request: Request, call_next):
            if request.method == "GET" and request.url.path != "/health":
                if not secrets.compare_digest(request.headers.get("X-API-Key", ""), api_key):
                    return JSONResponse({"detail": "invalid or missing X-API-Key"}, status_code=401)
            return await call_next(request)

    for router in (devices.router, telemetry.router, alarms.router, report.router):
        app.include_router(router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
