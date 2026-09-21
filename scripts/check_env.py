"""사전 과제용 환경 점검. 모두 OK 면 exit 0.  python scripts/check_env.py"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys


def check(name: str, ok: bool, hint: str = "") -> bool:
    print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f"   → {hint}" if not ok and hint else ""))
    return ok


def main() -> int:
    results = [check(f"Python {sys.version.split()[0]} >= 3.11", sys.version_info >= (3, 11), "Python 3.11 이상 설치")]
    for mod in ("fastapi", "uvicorn", "httpx", "pytest", "mcp", "equip_monitor"):
        try:
            importlib.import_module(mod)
            results.append(check(f"import {mod}", True))
        except ImportError:
            results.append(check(f"import {mod}", False, "pip install -r requirements.txt"))
    code_hint = 'VS Code 에서 Cmd+Shift+P → "Shell Command: Install \'code\' command in PATH"' if sys.platform == "darwin" else "code 설치 후 터미널 재시작"
    for tool, hint in (("git", "git 설치 후 터미널 재시작"), ("gh", "gh 설치 후 터미널 재시작"), ("code", code_hint)):
        results.append(check(f"{tool} on PATH", shutil.which(tool) is not None, hint))
    gh_ok = shutil.which("gh") is not None and subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0
    results.append(check("gh auth status", gh_ok, "gh auth login"))
    if shutil.which("code") is not None:
        try:
            out = subprocess.run(["code", "--list-extensions"], capture_output=True, text=True, timeout=20).stdout
            installed = {line.strip().lower() for line in out.splitlines()}
            results.append(check("GitHub Copilot Chat extension", "github.copilot-chat" in installed, 'GitHub Copilot Chat 확장을 설치하세요 (VS Code 확장 탭에서 "GitHub Copilot Chat")'))
        except Exception:
            results.append(check("GitHub Copilot Chat extension", False, "code --list-extensions 실행 실패"))
    print("\n모두 OK — 이 화면을 캡처해 제출하세요." if all(results) else "\nFAIL 항목을 해결한 뒤 다시 실행하세요.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
