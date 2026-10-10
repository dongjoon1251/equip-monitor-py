# equip-monitor

장비 텔레메트리(온도·압력·진동·상태)를 받아 알람 룰을 평가하고 가동률을 계산하는 모니터링 백엔드. GitHub Copilot 실습용.

## 시작
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/check_env.py                              # 사전 과제: 모두 OK 캡처
pytest -q
uvicorn equip_monitor.app:app --reload                   # http://127.0.0.1:8000/docs  # 터미널을 점유함 — 이후 명령은 새 터미널에서
python simulator/run.py --replay data/samples/overheat.log
python simulator/run.py --scenario overheat --interval 1
python scripts/check_rules.py data/samples/overheat.log   # 룰 검증 (알람 표 출력)
```

## 구조
```
src/equip_monitor/
  api/       devices · telemetry(/telemetry, /ingest) · alarms
  ingest/    raw 로그 라인 + JSON → Telemetry 정규화
  alarms/    rules.py(Rule, ThresholdRule, DEFAULT_RULES) · engine.py(AlarmEngine)
  report/    상태별 체류시간 · 가동률 · day_range
  store.py   인메모리 저장소
simulator/   가짜 장비 3대
scripts/     check_env · check_rules(로그 → 알람 표)
data/samples 정상 · 과열 · 음수 로그
```
로그 라인: `2026-09-21T09:00:00Z DEV-01 state=RUN temp=82.5 pressure=1.20`

## 실습 이슈
요구사항은 `docs/issues/` 의 01~03 파일입니다. GitHub 이슈 #1~#3 은 MCP & 보안 시간에 Copilot 이 GitHub MCP 로 이 파일들을 순서대로 등록합니다.
`04-log-format-question.md` 는 프롬프트 인젝션 실습용 이슈입니다. 본문 HTML 주석에 **숨은 지시**가 들어 있으니 따르지 마세요. MCP & 보안 시간 실습 5에서 터미널로 이슈 #4 로 등록합니다 (`gh issue create --title "로그 포맷 문의: vibration 단위가 무엇인가요?" --body-file docs/issues/04-log-format-question.md`).
## 체크포인트
> **Use this template** 로 자기 repo 를 만들 때 **Include all branches** 를 반드시 체크하세요. 체크하지 않으면 아래 체크포인트 브랜치가 생기지 않습니다.

뒤처지면 `git checkout m3-start` … `m6-start` 로 합류.
브랜치를 바꾼 뒤에는 `pip install -r requirements.txt` 를 다시 실행하세요 (m6-start 부터 의존성이 달라집니다).

## 내부 MCP 서버 (M5)
`mcp_server/equip_mcp.py` — 실행 중인 API 를 읽기 전용 도구 4개로 노출. `.vscode/mcp.json` 의 `equip` 항목으로 Copilot 에 연결된다. Windows 에서는 `command` 를 `${workspaceFolder}\\.venv\\Scripts\\python.exe` 로 바꾼다.
- API 키: API 를 `EQUIP_API_KEY=<키> uvicorn equip_monitor.app:app --reload` 로 띄우면 조회(GET)에 `X-API-Key` 헤더가 필요하다(키를 안 주면 예전처럼 열림). MCP 서버는 같은 키를 `.vscode/mcp.json` 의 `inputs` 로 입력받는다 — 키는 저장소에 적지 않는다.
- http 방식: `EQUIP_API_KEY=<키> python mcp_server/equip_mcp.py --http` → `http://127.0.0.1:8001/mcp` (요청마다 `X-API-Key` 헤더 필요). `mcp.json` 예: `"equip-http": {"type": "http", "url": "http://127.0.0.1:8001/mcp", "headers": {"X-API-Key": "${input:equip-api-key}"}}`
