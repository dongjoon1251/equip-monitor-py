---
applyTo: "tests/**"
---
# 테스트 규약
- pytest 함수 스타일. 파일명 `test_<모듈>.py`, 함수명은 동작을 문장으로(`test_threshold_rule_fires_at_limit_not_below`).
- 시간은 `tests/helpers.py` 의 `T0`, `at(minutes)`, `tele(...)` 로 만든다. `datetime.now()` 금지.
- 경계값은 3종(미만 / 정확히 경계 / 초과)을 반드시 나눠 검증한다.
- 전역 `store` 는 `conftest.py` 가 매 테스트 전후 `reset()` 한다. 필요하면 `Store()` 를 새로 만들어 격리한다.
- 네트워크·파일시스템 접근 금지. API 는 `fastapi.testclient.TestClient` 로만 호출.
- 하나의 테스트는 하나의 동작만 검증한다.
