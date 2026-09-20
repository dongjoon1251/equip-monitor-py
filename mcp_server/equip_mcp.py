"""equip-monitor 를 Copilot Agent 에 노출하는 읽기 전용 MCP 서버 (stdio).

실행 중인 API(기본 http://127.0.0.1:8000, 환경변수 EQUIP_API) 를 HTTP 로 조회한다.
VS Code: .vscode/mcp.json 의 "equip" 항목으로 등록된다.
"""
from __future__ import annotations

import os

import httpx
from mcp.server.mcpserver import MCPServer  # ponytail: installed mcp==2.2.0 renamed FastMCP -> MCPServer; API (tool()/list_tools()/run()) is unchanged

BASE = os.environ.get("EQUIP_API", "http://127.0.0.1:8000")
mcp = MCPServer("equip-monitor")


def _get(path: str, **params: object) -> object:
    r = httpx.get(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=5)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def list_devices() -> list[dict]:
    """등록된 장비와 현재 상태 목록."""
    return _get("/devices")


@mcp.tool()
def get_alarms(device_id: str | None = None, since: str | None = None) -> list[dict]:
    """알람 목록. since 는 ISO-8601 UTC (예: 2026-09-21T09:00:00Z)."""
    return _get("/alarms", device_id=device_id, since=since)


@mcp.tool()
def get_recent_telemetry(device_id: str, limit: int = 20) -> list[dict]:
    """장비의 최근 텔레메트리 limit 개 (오래된 것부터)."""
    return _get(f"/devices/{device_id}/telemetry")[-limit:]


@mcp.tool()
def get_uptime(from_date: str, to_date: str, device_id: str | None = None) -> list[dict]:
    """기간(YYYY-MM-DD, 양 끝 포함)의 장비별 상태 체류시간과 가동률."""
    return _get("/report/uptime", **{"from": from_date, "to": to_date, "device_id": device_id})


if __name__ == "__main__":
    mcp.run()  # stdio
