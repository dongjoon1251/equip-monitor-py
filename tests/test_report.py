from datetime import date, datetime
from zoneinfo import ZoneInfo

from equip_monitor.models import DeviceState
from equip_monitor.report.uptime import day_range, state_durations, uptime_ratio
from helpers import at, tele

RUN, IDLE, DOWN = DeviceState.RUN, DeviceState.IDLE, DeviceState.DOWN


def test_state_carries_until_next_sample():
    tel = [tele(minutes=0, state=RUN), tele(minutes=30, state=IDLE)]
    d = state_durations(tel, at(0), at(60))
    assert d == {"RUN": 1800.0, "IDLE": 1800.0, "DOWN": 0.0, "MAINT": 0.0}


def test_window_clips_samples_outside_range():
    tel = [tele(minutes=-30, state=DOWN), tele(minutes=10, state=RUN), tele(minutes=70, state=IDLE)]
    d = state_durations(tel, at(0), at(60))
    assert d["DOWN"] == 600.0 and d["RUN"] == 3000.0 and d["IDLE"] == 0.0


def test_uptime_ratio():
    tel = [tele(minutes=0, state=RUN), tele(minutes=15, state=DOWN)]
    assert uptime_ratio(tel, at(0), at(60)) == 0.25
    assert uptime_ratio([], at(0), at(0)) == 0.0


def test_day_range_includes_early_morning_kst():
    # 2026-09-21 05:00 KST 에 시작한 가동은 21일 리포트에 포함되어야 한다
    start, end = day_range(date(2026, 9, 21))
    assert start <= datetime(2026, 9, 21, 5, 0, tzinfo=ZoneInfo("Asia/Seoul")) < end
