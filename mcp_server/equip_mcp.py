"""equip-monitor 를 Copilot Agent 에 노출하는 읽기 전용 MCP 서버 (stdio).

실행 중인 API(기본 http://127.0.0.1:8000, 환경변수 EQUIP_API) 를 HTTP 로 조회한다.
VS Code: .vscode/mcp.json 의 "equip" 항목으로 등록된다.
"""
from __future__ import annotations

import os
import sys

import httpx
from mcp.server.mcpserver import MCPServer  # ponytail: mcp>=2.0 API — MCPServer's tool()/list_tools()/run() surface is what this module targets
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

BASE = os.environ.get("EQUIP_API", "http://127.0.0.1:8000")
API_KEY = os.environ.get("EQUIP_API_KEY", "")
mcp = MCPServer("equip-monitor")
READ_ONLY = ToolAnnotations(read_only_hint=True)


def _get(path: str, **params: object) -> object:
    # 일반 예외는 모델에 "Error executing tool" 만 보인다 → 원인을 ToolError 로 알려 준다
    try:
        r = httpx.get(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None},
                      headers={"X-API-Key": API_KEY}, timeout=5)
    except httpx.ConnectError:
        raise ToolError(f"equip-monitor API({BASE})에 연결할 수 없다 — 서버가 꺼져 있다.")
    if r.status_code == 401:
        raise ToolError("API 키가 틀렸다(401) — mcp.json inputs 의 Edit 로 다시 입력해야 한다.")
    r.raise_for_status()
    return r.json()


@mcp.tool(annotations=READ_ONLY)
def list_devices() -> list[dict]:
    """등록된 장비와 현재 상태 목록."""
    return _get("/devices")


@mcp.tool(annotations=READ_ONLY)
def get_alarms(device_id: str | None = None, since: str | None = None) -> list[dict]:
    """알람 목록. since 는 ISO-8601 UTC (예: 2026-09-21T09:00:00Z)."""
    return _get("/alarms", device_id=device_id, since=since)


@mcp.tool(annotations=READ_ONLY)
def get_recent_telemetry(device_id: str, limit: int = 20) -> list[dict]:
    """장비의 최근 텔레메트리 limit 개 (오래된 것부터)."""
    return _get(f"/devices/{device_id}/telemetry")[-limit:]


@mcp.tool(annotations=READ_ONLY)
def get_uptime(from_date: str, to_date: str, device_id: str | None = None) -> list[dict]:
    """기간(YYYY-MM-DD, 양 끝 포함)의 장비별 상태 체류시간과 가동률."""
    return _get("/report/uptime", **{"from": from_date, "to": to_date, "device_id": device_id})


def http_app():
    """http 방식 앱 — 모든 요청에 X-API-Key 헤더(= EQUIP_API_KEY)를 요구한다."""
    import secrets

    from starlette.responses import JSONResponse

    inner = mcp.streamable_http_app()

    async def app(scope, receive, send):
        if scope["type"] == "http":
            given = dict(scope["headers"]).get(b"x-api-key", b"").decode()
            if not secrets.compare_digest(given, API_KEY):
                await JSONResponse({"detail": "invalid or missing X-API-Key"}, status_code=401)(scope, receive, send)
                return
        await inner(scope, receive, send)

    return app


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("EQUIP_API_KEY 가 없습니다 — .vscode/mcp.json 의 inputs 로 입력하세요.")
    if "--http" in sys.argv:
        # 원격(http) 방식: 이 프로세스를 먼저 띄워 두고 VS Code 는 URL + 키 헤더로 접속한다
        import uvicorn

        uvicorn.run(http_app(), host="127.0.0.1", port=int(os.environ.get("EQUIP_MCP_PORT", "8001")))
    else:
        mcp.run()  # stdio: VS Code 가 직접 이 프로세스를 실행
