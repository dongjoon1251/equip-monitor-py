from fastapi.testclient import TestClient

from equip_monitor.app import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_post_telemetry_raises_alarm_and_lists_it():
    body = [{"device_id": "DEV-01", "ts": "2026-09-21T09:00:00Z", "metrics": {"Temp": 96}, "state": "RUN"}]
    r = client.post("/telemetry", json=body)
    assert r.status_code == 202
    assert r.json()["accepted"] == 1
    assert r.json()["alarms"][0]["rule"] == "temp-critical"
    alarms = client.get("/alarms", params={"device_id": "DEV-01"}).json()
    assert alarms[0]["severity"] == "CRITICAL" and alarms[0]["acked"] is False
    assert client.post(f"/alarms/{alarms[0]['id']}/ack").json()["acked"] is True
    assert client.post("/alarms/999/ack").status_code == 404


def test_ingest_text_lines_autoregisters_device():
    text = "2026-09-21T09:00:00Z DEV-07 state=RUN temp=50\n2026-09-21T09:01:00Z DEV-07 state=IDLE temp=51\n"
    r = client.post("/ingest", content=text, headers={"content-type": "text/plain"})
    assert r.status_code == 202 and r.json()["accepted"] == 2
    assert client.get("/devices/DEV-07").json()["state"] == "IDLE"
    since = client.get("/devices/DEV-07/telemetry", params={"since": "2026-09-21T09:01:00Z"}).json()
    assert len(since) == 1 and since[0]["metrics"] == {"temp": 51.0}


def test_ingest_malformed_returns_422():
    r = client.post("/ingest", content="not a line", headers={"content-type": "text/plain"})
    assert r.status_code == 422


def test_devices_crud():
    assert client.post("/devices", json={"id": "DEV-01", "name": "챔버 1", "location": "A동"}).status_code == 201
    assert [d["id"] for d in client.get("/devices").json()] == ["DEV-01"]
    assert client.get("/devices/NOPE").status_code == 404
