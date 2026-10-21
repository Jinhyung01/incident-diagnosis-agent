# 발표 보완 시나리오

2026-10-21. 실제 개선 앱의 HTTP 프록시·SSE·LangGraph·MCP를 사용했다. 답변을 미리 만들거나 재생하지 않았다. 기본 앱 설정과 다른 제어 조건을 아래에 표시한다.

| 사례 | 조건 | 실제 결과 |
|---|---|---|
| 미등록 대상 | billing-service 입력 | 다른 서비스 조회 없음, 등록 서비스 이름 확인 요청 |
| 정보 부족 | web-01 status=degraded, alerts=[] fixture | 정보 부족 안내, 매뉴얼 적용 없음 |
| 시간 초과 | 보고 생성 의존성 30초 지연, 요청 상한 8초 | 8.003초에 시간 제한 안내, 수집된 CPU 91.0%·메모리 55.0% 보존 |

일반 설정은 호출 25초·요청 60초·512토큰·최대 2회 작성이다. 시간 초과 화면의 8초는 재현을 위한 시험 설정이다. 해당 요청은 검증된 LLM 보고서를 완성하지 못했으며 수집 관측과 문서 원문만 안내한다.

원시 이벤트는 unknown.json, insufficient.json, timeout.json에 저장했다. fixture는 monitoring-fixture.json, 재현 진입점은 day2/scripts/serve_presentation_scenarios.py다. UI는 8705, 백엔드는 8205 포트를 사용하고 별도 SQLite DB를 쓴다. 단위 테스트 31개도 다시 통과했다(day2/tests/unit-tests-presentation.txt).

## 20개 비교 결과와의 구분

20개 비교는 저장된 개선 버전의 측정 결과다. 이후 agent/evidence.py의 미등록 확인 요청, server.py의 시간 초과·오류 안내 문장과 import 정렬을 보완했다. 측정 당시 구현 해시와 달라진 파일은 agent/evidence.py, server.py다. 대상 선택·검색·검증·생성 상한 로직은 변경하지 않았다.

이 보완 뒤 전체 20개 시간 통계를 다시 측정하지 않았다. 기존 수치는 이전 측정으로 유지하고, 안내 문구와 세 분기 동작은 위 별도 실제 UI 시험과 단위 테스트로 확인했다. 새 시험을 기존 비교 통계에 합산하지 않는다.
