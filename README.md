# equip-monitor

장비 텔레메트리(온도·압력·진동·상태)를 받아 알람 룰을 평가하고 가동률을 계산하는 모니터링 백엔드. GitHub Copilot 실습용.

## 시작
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/check_env.py                              # 사전 과제: 모두 OK 캡처
pytest -q
uvicorn equip_monitor.app:app --reload                   # http://127.0.0.1:8000/docs
python simulator/run.py --replay data/samples/overheat.log
python simulator/run.py --scenario overheat --interval 1
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
scripts/     check_env · seed(이슈 생성) · check_rules(로그 → 알람 표)
data/samples 정상 · 과열 · 음수 로그
```
로그 라인: `2026-09-21T09:00:00Z DEV-01 state=RUN temp=82.5 pressure=1.20`

## 실습 이슈
`python scripts/seed.py` 로 생성. 본문은 `docs/issues/`.

## 체크포인트
뒤처지면 `git checkout m3-start` … `m6-start` 로 합류.
