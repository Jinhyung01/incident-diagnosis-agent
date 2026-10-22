# 발표 범위와 실제 구현 대응

## 주요 기능

| 계획 | 실제 구현 | 발표 |
|---|---|---|
| 자연어 장애 진단 요청 | 기존 베이스의 FastAPI·LangGraph·MCP 기반을 활용해 대상·상태·보고 흐름 개선 | 2장 소개,5~20장 전후 |
| 다중 서비스 조사 | 등록 대상 전체를 직접 추출하고 대상별 조회·오류 분리 | 5~10장 |
| 답변 근거 표시 | 실제 수집 객체로 서비스·지표·문서·미확인 항목 구성 | 7·10·22장 |

## 발표할 개선4개

| 개선 | 실제로 바꾼 처리 | 코드 | 발표 |
|---|---|---|---|
| 대상 누락 방지 | 요청 대상 추출 후 모델 tasks 대신 대상별 조회 작업 재구성 | [targets.py](../all_total_vue_student/agent/targets.py), [research.py](../all_total_vue_student/agent/research.py) | 5~10장 |
| 미등록 서비스 처리 | 등록 목록 대조, 미등록·대상 없음은 조회·보고 생성 생략 후 확인 요청 | [targets.py](../all_total_vue_student/agent/targets.py), [nodes.py](../all_total_vue_student/agent/nodes.py) | 11~14장 |
| 매뉴얼 선택 개선 | 상태·활성 알림으로 분기하고 investigate 서비스만 검색 | [evidence.py](../all_total_vue_student/agent/evidence.py), [research.py](../all_total_vue_student/agent/research.py) | 15~16장 |
| 답변 검증 강화 | JSON 출력·근거 대조·절차 원문 렌더링, 원인 확정 거절 | [reporting.py](../all_total_vue_student/agent/reporting.py), [validation.py](../all_total_vue_student/agent/validation.py) | 17~18장 |

## 계획한 추가 기능 3개

| 추가 | 구현과 증빙 | 발표 |
|---|---|---|
| RAG 매뉴얼 검색 | bge-m3·SQLite 코사인 검색 후 MCP Resource 원문 연결 | 21장 |
| 근거·미확인 화면 | FinalAnswer.evidence를 실제 수집 객체로 구성하고 UI 표 렌더링 | 22장 |
| 회귀·동일 입력 비교 | 고정질문20개·호출/문서/시간 기록 집계, 단위31개 | 23~24장 |

## 그 밖에 보완한 부분

- **이름 응답:** 사용자 역할의 선언만 대화 이력에서 읽도록 보완했다. 기존 SQLite 이력을 활용하며 새 주요 기능으로 세지 않는다.19~20장 전후 화면과 보충 노트에 포함했다.
- **실행 보호:** 사용 중인 포트의 프로세스를 임의로 종료하거나 기존 세션DB를 삭제하지 않도록 실행 스크립트를 바꿨다. [변경 범위](../docs/CHANGES.md)에 정리한 보조 변경이며 장애 진단 기능을 하나 더 추가했다고 세지 않는다.
- 서비스별 조회 오류 격리는 대상별 조회의 내부 보강이며 독립 추가 기능으로 늘리지 않는다.

계획에만 남은 항목을 구현 완료로 표시하지 않는다. 실제 자료는 [질문별 캡처·원시 기록](EVIDENCE_INDEX.md)에 연결한다.

## 사용 기술과 실제 변경

4장에 기술명·적용 방식·해결한 문제를 표로 설명하고 각 기능의 실제 화면으로 연결한다.

| 기술 | 실제 변경과 코드 | 실행 증빙 |
|---|---|---|
| MCP | [mcp_server.py](../all_total_vue_student/mcp_server.py)의 search_runbooks Tool 추가, 기존 모니터링·Resource 조회 활용 | 21장 RAG 실행 |
| RAG | [retrieval.py](../all_total_vue_student/agent/retrieval.py)의 bge-m3 임베딩·SQLite 캐시·코사인 검색, [research.py](../all_total_vue_student/agent/research.py)의 원문 연결 | 16·21장 매뉴얼 선택 |
| LangGraph·모듈화 | [graph.py](../all_total_vue_student/agent/graph.py)·[nodes.py](../all_total_vue_student/agent/nodes.py)의 범위·검색 노드와 검증 반복, 대상·수집·보고·검증 파일 분리 | 6·16·18장 구현 단계 |
| 의존성 주입 | 기존 [SupervisorDeps](../all_total_vue_student/agent/deps.py)에 searcher 추가, MCP·고정 검색 어댑터 교체 | 21장 검색, 23장 고정 평가 |
| 단위 테스트·평가 | [test_core.py](../all_total_vue_student/tests/test_core.py)의 31개 분기 시험, [평가 정의](../day1/evaluation/cases.json)의 20개 입력과 결과 집계 | 23~24장 보고서, 원시 결과·시험 기록 |

기존 LangSmith traceable 코드는 유지하지만 새 추적 분석 성과에는 포함하지 않는다. 전문 Multi-Agent 서브그래프를 추가한 구현도 아니다.
