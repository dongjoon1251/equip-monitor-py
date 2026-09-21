---
name: alarm-rule
description: equip-monitor 에 알람 룰을 추가하거나 수정할 때 사용. rules.py 구현 → DEFAULT_RULES 등록 → 경계 테스트 → check_rules.py 검증까지의 절차와 판정 기준을 담는다. "알람", "룰", "임계치", "지속", "threshold" 요청에 적용.
---
# 알람 룰 추가/수정 절차

## 1. 룰 설계 체크리스트 (구현 전에 답을 정한다)
| 항목 | 질문 | 이 repo 의 기본값 |
|---|---|---|
| 임계 | 어떤 metric, 어떤 비교(≥, ≤)? | `metrics[...]` 없으면 무시(None) |
| 지속 | 즉시인가, N초 지속인가? | 지속이면 텔레메트리 `ts` 차이로만 판단 |
| 회복 | 조건이 풀리면 어떻게 되나? | 다음 발생 시 다시 알람 |
| 중복 | 지속 중 매 샘플마다 알람인가? | 아니오 — 경계를 처음 넘는 샘플에서 1회 |
| 심각도 | INFO / WARNING / CRITICAL | 명시 없으면 WARNING |

## 2. 구현
1. `src/equip_monitor/alarms/rules.py` 에 `@dataclass` 클래스 추가. `name`, `evaluate(current, history) -> Finding | None` 구현. `history` 는 같은 장비의 이전 텔레메트리(오름차순, current 미포함).
2. `DEFAULT_RULES` 끝에 등록. 룰 이름은 `<metric>-<의미>` 소문자 하이픈.
3. 메시지 형식: `"<metric> <조건> [for N min]"`. 값은 `:g` 포맷.

## 3. 테스트 (`tests/test_rules.py`)
- `AlarmEngine(Store(), [룰])` 로 격리. 시간은 `helpers.tele(minutes=..., temp=...)`.
- 경계 3종: 조건 미만 / 정확히 경계 / 초과.
- 지속 룰이면 추가: 지속시간 - 1초, 정확히 지속시간, 지속 중 재알람 없음, 회복 후 재발.

## 4. 검증 (반드시 실행하고 출력을 응답에 붙인다)
```
pytest -q   # (전체 스위트 — 새 룰을 DEFAULT_RULES 에 넣으면 tests/test_engine.py 의 룰 이름 목록 테스트도 갱신해야 한다)
python scripts/check_rules.py data/samples/overheat.log
```
`overheat.log` 기대 결과: `temp-sustained` 09:07 · 09:15, `temp-critical` 09:16. 기대와 다르면 룰을 고치고 다시 실행한다. 3회 실패하면 멈추고 사용자에게 보고한다.

## 5. 하지 않는 것
- 라우터·store 수정 (룰은 `rules.py` 안에서 끝난다)
- `datetime.now()` 사용
- 기존 룰 이름 변경
