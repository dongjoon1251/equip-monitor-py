from datetime import timezone

import pytest

from equip_monitor.ingest.parser import normalize, parse_line, parse_lines
from equip_monitor.models import DeviceState, Telemetry
from helpers import T0


def test_parse_line_basic():
    t = parse_line("2026-09-21T09:00:00Z DEV-01 state=RUN temp=82.5 pressure=1.20")
    assert t.device_id == "DEV-01"
    assert t.ts == T0
    assert t.state == DeviceState.RUN
    assert t.metrics == {"temp": 82.5, "pressure": 1.2}


def test_parse_line_defaults_state_to_idle_and_lowercases_keys():
    t = parse_line("2026-09-21T09:00:00Z DEV-02 Temp=70")
    assert t.state == DeviceState.IDLE
    assert t.metrics == {"temp": 70.0}


def test_parse_lines_skips_blank_and_comment_lines():
    text = "# sample\n\n2026-09-21T09:00:00Z DEV-01 temp=1\n2026-09-21T09:01:00Z DEV-01 temp=2\n"
    assert [t.metrics["temp"] for t in parse_lines(text)] == [1.0, 2.0]


@pytest.mark.parametrize("line", ["garbage", "2026-09-21T09:00:00 DEV-01 temp=1", "2026-09-21T09:00:00Z DEV-01 temp=hot"])
def test_parse_line_rejects_malformed(line):
    with pytest.raises(ValueError):
        parse_line(line)


def test_kst_timestamp_is_converted_to_utc():
    t = parse_line("2026-09-21T18:00:00+09:00 DEV-01 temp=1")
    assert t.ts == T0 and t.ts.tzinfo == timezone.utc


def test_normalize_lowercases_metric_keys():
    t = Telemetry(device_id="DEV-01", ts=T0, metrics={"Temp": 1.0})
    assert normalize(t).metrics == {"temp": 1.0}
