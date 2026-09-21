"""현재 repo 에 실습용 라벨·이슈를 만든다 (gh CLI 로그인 필요).

  python scripts/seed.py                   # 이슈 #1~#3
  python scripts/seed.py --with-injection  # 강사 repo 전용: #4 인젝션 시연 이슈 추가
                                           # (이슈 #4 본문은 강사용 solution repo 에만 있음 → --injection-file 로 경로 지정)
"""
from __future__ import annotations

import argparse
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
INJECTION_DEFAULT = "docs/issues/04-log-format-question.md"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout.strip()


def main(with_injection: bool, injection_file: Path = Path(INJECTION_DEFAULT)) -> int:
    plan = [(ISSUES / filename, labels) for filename, labels in PLAN]
    if with_injection:
        if not injection_file.is_file():
            print(f"인젝션 데모 이슈 파일이 없습니다: {injection_file}", file=sys.stderr)
            print("강사용 solution repo 의 docs/issues/04-log-format-question.md 경로를 --injection-file 로 지정하세요", file=sys.stderr)
            return 2
        plan.append((injection_file, "demo"))
    for name, color in LABELS.items():
        gh("label", "create", name, "--color", color, "--force")
    for path, labels in plan:
        title = path.read_text(encoding="utf-8").splitlines()[0].lstrip("#").strip()
        print(gh("issue", "create", "--title", title, "--body-file", str(path), "--label", labels))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub 라벨·실습 이슈 생성 (gh CLI 필요, 한 번만 실행)")
    parser.add_argument("--with-injection", action="store_true", help="이슈 #4(프롬프트 인젝션 데모)도 생성")
    parser.add_argument("--injection-file", default=INJECTION_DEFAULT, help=f"이슈 #4 본문 파일 경로 (기본: {INJECTION_DEFAULT})")
    args = parser.parse_args()
    try:
        sys.exit(main(args.with_injection, Path(args.injection_file)))
    except subprocess.CalledProcessError as exc:
        print(f"gh 명령 실패: {exc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
