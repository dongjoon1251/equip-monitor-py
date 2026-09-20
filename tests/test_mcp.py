import asyncio

from mcp_server.equip_mcp import mcp


def test_mcp_exposes_read_only_tools():
    tools = asyncio.run(mcp.list_tools())
    assert sorted(t.name for t in tools) == ["get_alarms", "get_recent_telemetry", "get_uptime", "list_devices"]
