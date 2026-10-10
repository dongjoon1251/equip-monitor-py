"""postToolUse hook: 파일을 고친 직후 전체 테스트를 돌려 결과를 모델에게 돌려준다."""
import json
import os
import subprocess
import sys
from pathlib import Path

LOG = Path(".github/hooks/hook.log")
python = next((p for p in (".venv/Scripts/python.exe", ".venv/bin/python") if Path(p).exists()), sys.executable)
env = {**os.environ, "PYTHONPATH": "src", "TZ": "UTC0"}  # CI 와 같은 UTC 에서 검증 (Windows 도 이해하는 표기)
r = subprocess.run([python, "-m", "pytest", "-q", "-p", "no:cacheprovider"], capture_output=True, text=True, env=env, timeout=50)
if "No module named pytest" in r.stderr:  # pytest 가 없는 환경(예: 설치 전 cloud agent)에서는 조용히 넘어감
    sys.exit(0)
last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
with LOG.open("a", encoding="utf-8") as f:
    f.write(f"postToolUse pytest(UTC): {last}\n")
if r.returncode != 0:
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAILED")][:5]
    msg = ("[Harness] 방금 변경 후 UTC 시간대 pytest 가 실패한다: " + last + "\n" + "\n".join(fails)
           + "\n이번 작업과 관계없는 실패면 고치지 말고 보고만 하라.")
else:
    msg = "[Harness] 방금 변경 후 UTC 시간대 pytest 통과: " + last
print(json.dumps({"additionalContext": msg}, ensure_ascii=False))
