"""로그 파일을 룰 엔진에 흘려 발생 알람을 표로 출력한다. Skill 'alarm-rule' 의 검증 스크립트.

  python scripts/check_rules.py data/samples/overheat.log
"""
from __future__ import annotations

import sys
from pathlib import Path

from equip_monitor.alarms.engine import AlarmEngine
from equip_monitor.ingest.parser import parse_lines
from equip_monitor.store import Store


def main(path: str) -> int:
    engine = AlarmEngine(Store())
    alarms = [a for t in parse_lines(Path(path).read_text(encoding="utf-8")) for a in engine.process(t)]
    print(f"{'ts':20} {'device':8} {'rule':20} {'severity':9} message")
    for a in alarms:
        print(f"{a.ts:%Y-%m-%dT%H:%M:%SZ} {a.device_id:8} {a.rule:20} {a.severity.value:9} {a.message}")
    print(f"-- {len(alarms)} alarm(s)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python scripts/check_rules.py <log 파일>", file=sys.stderr)
        sys.exit(2)
    log_path = sys.argv[1]
    if not Path(log_path).exists():
        print(f"파일을 찾을 수 없습니다: {log_path}", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(log_path))
