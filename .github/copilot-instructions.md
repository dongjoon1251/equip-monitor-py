# equip-monitor 작업 지침

## 프로젝트
장비 텔레메트리 수집 → 알람 룰 평가 → 가동률 리포트를 제공하는 FastAPI 백엔드. 저장은 인메모리(`store.py`).
- `api/` 라우터만. 비즈니스 로직은 넣지 않는다.
- `ingest/parser.py` raw 라인·JSON → `Telemetry` 정규화의 단일 진입점.
- `alarms/rules.py` 룰 정의(`Rule` 프로토콜, `DEFAULT_RULES`), `alarms/engine.py` 평가·저장.
- `report/uptime.py` 상태별 체류시간·가동률·`day_range`.

## 규약
- 모든 datetime 은 timezone-aware UTC. `datetime.now()`·naive datetime 금지. 룰의 시간 판단은 텔레메트리 `ts` 기준.
- 새 알람 룰: `rules.py` 에 `@dataclass` 로 구현 → `DEFAULT_RULES` 등록 → `tests/test_rules.py` 경계 테스트 → `python scripts/check_rules.py data/samples/overheat.log` 로 확인.
- 저장소 접근은 `store` 메서드로만. 라우터에서 `store.devices` 같은 내부 dict 직접 접근 금지.
- 응답/요청 모델은 `models.py` 의 pydantic 모델을 재사용.
- 새 의존성 추가 금지(`requirements.txt` 고정). 시크릿·토큰 하드코딩 금지.

## 작업 방식
- 변경 전 관련 테스트를 먼저 실행하고, 변경 후 `pytest -q` 전체를 돌린다.
- 요구가 모호하면 확인 질문 대신 가정을 한 줄로 밝히고 진행한다.
- 한 응답에 변경 파일 목록과 테스트 결과 요약을 포함한다.
- 알람 관련 작업은 `src/equip_monitor/alarms/` 부터 읽는다. 전체 검색(`#codebase`)은 위치를 모를 때 한 번만.

## PR · Jira
- Jira 작업은 `feat/<Jira 키>` 브랜치에서 구현하고(`/jira-implement`), 커밋 메시지는 `<Jira 키> feat: …` 한 줄. PR 은 `/pr-create` 로 만든다(초안 → 사람 승인 → push → PR).
- Jira 작업에서 시작한 일은 PR 제목 맨 앞에 Jira 키를 쓴다(예: `KAN-5 feat: 알람 웹훅 알림`). 설명 `Jira:` 칸에 Jira · Confluence 링크.
- GitHub 이슈를 닫는 PR 은 설명에 `Closes #N` 을 이슈마다 쓴다.
- 머지는 사람이 한다. 에이전트는 PR 을 열고 리뷰 · CI 결과를 정리하는 데까지만 한다.
- Jira 상태는 Actions(`jira-sync.yml` · `jira-deploy.yml`)가 바꾼다. 에이전트가 Jira 를 직접 Done 으로 바꾸지 않는다.
