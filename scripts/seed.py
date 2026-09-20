"""현재 repo 에 실습용 라벨·이슈를 만든다 (gh CLI 로그인 필요).

  python scripts/seed.py                   # 이슈 #1~#3
  python scripts/seed.py --with-injection  # 강사 repo 전용: #4 인젝션 시연 이슈 추가
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ISSUES = Path(__file__).resolve().parent.parent / "docs" / "issues"
LABELS = {"feature": "0E8A16", "bug": "D73A4A", "practice": "1D76DB", "demo": "5319E7"}
PLAN = [
    ("01-sustained-alarm.md", "feature,practice"),
    ("02-uptime-report.md", "feature,practice"),
    ("03-negative-values.md", "bug,practice"),
]


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout.strip()


def main(with_injection: bool) -> int:
    for name, color in LABELS.items():
        gh("label", "create", name, "--color", color, "--force")
    plan = PLAN + ([("04-log-format-question.md", "demo")] if with_injection else [])
    for filename, labels in plan:
        path = ISSUES / filename
        title = path.read_text(encoding="utf-8").splitlines()[0].lstrip("#").strip()
        print(gh("issue", "create", "--title", title, "--body-file", str(path), "--label", labels))
    return 0


if __name__ == "__main__":
    sys.exit(main("--with-injection" in sys.argv[1:]))
