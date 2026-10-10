"""사전 과제용 환경 점검. 모두 OK 면 exit 0.  python scripts/check_env.py"""
from __future__ import annotations

import importlib
import os
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
    # gh 로그인은 선택: PR 생성에만 쓰고, GitHub 웹으로 대신할 수 있다 → 실패해도 WARN.
    gh_ok = shutil.which("gh") is not None and subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0
    print("[OK ] gh auth status" if gh_ok else "[WARN] gh auth status   → (선택) gh auth login — PR 생성에 사용, 안 되면 GitHub 웹에서 직접 해도 됩니다")
    code_path = shutil.which("code")
    if code_path is not None:
        try:
            proc = subprocess.run([code_path, "--list-extensions"], capture_output=True, text=True, timeout=20)
            if proc.returncode == 0:
                installed = {line.strip().lower() for line in proc.stdout.splitlines()}
                # VS Code 1.11x 부터 Copilot Chat 은 VS Code 에 내장 → 확장 목록에 안 나온다. 설치본의 내장 확장 폴더도 확인.
                install_dir = os.path.dirname(os.path.dirname(os.path.realpath(code_path)))
                app_dirs = [install_dir]
                with os.scandir(install_dir) as entries:
                    app_dirs.extend(entry.path for entry in entries if entry.is_dir())
                builtin = any(
                    os.path.isdir(os.path.join(app_dir, *sub, "copilot"))
                    for app_dir in app_dirs
                    for sub in (("extensions",), ("resources", "app", "extensions"))
                )
                results.append(check("GitHub Copilot Chat (확장 또는 VS Code 내장)", "github.copilot-chat" in installed or builtin, 'VS Code 를 최신으로 업데이트하거나, 확장 탭에서 "GitHub Copilot Chat" 설치'))
            else:
                detail = proc.stderr.strip() or proc.stdout.strip() or f"종료 코드 {proc.returncode}"
                results.append(check("GitHub Copilot Chat extension", False, f"code --list-extensions 실패: {detail}"))
        except subprocess.TimeoutExpired:
            results.append(check("GitHub Copilot Chat extension", False, "code --list-extensions 가 20초 안에 응답하지 않음"))
        except OSError as exc:
            results.append(check("GitHub Copilot Chat extension", False, f"code 실행 실패: {exc}"))
    print("\n모두 OK — 이 화면을 캡처해 제출하세요." if all(results) else "\nFAIL 항목을 해결한 뒤 다시 실행하세요.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
