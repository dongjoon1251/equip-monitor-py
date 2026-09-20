"""FastAPI 앱 조립. 실행: uvicorn equip_monitor.app:app --reload"""
from __future__ import annotations

from fastapi import FastAPI

from .api import alarms, devices, report, telemetry


def create_app() -> FastAPI:
    app = FastAPI(title="equip-monitor", version="0.1.0")
    for router in (devices.router, telemetry.router, alarms.router, report.router):
        app.include_router(router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
