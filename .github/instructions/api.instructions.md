---
applyTo: "src/equip_monitor/api/**"
---
# API 규약
- 라우터는 도메인별 파일 하나, `router = APIRouter(prefix=..., tags=[...])`. `app.py::create_app` 에 등록.
- 경로·쿼리의 datetime 은 `models.ensure_utc` 를 거친다.
- 없는 리소스는 `HTTPException(404, "<resource> not found")`, 입력 오류는 422.
- 응답 타입 힌트는 `models.py` 의 모델(또는 그 list)로 명시한다. 새 응답 스키마가 필요하면 `models.py` 에 추가.
- 계산 로직은 `report/`·`alarms/` 로 위임하고 라우터는 조립만 한다.
