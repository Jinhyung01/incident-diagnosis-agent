# 질문·응답과 개선 결과의 증빙

현재 자료는 [발표 본문](../output/presentation/incident-diagnosis-agent-charts.pptx)이다. 원래 사용자 PNG7개와 같은 질문의 개선 결과를 수정·자르기 없이 사용한다. 최초 지표와 고정 평가의 값 차이는 성능 개선으로 해석하지 않는다.

## 최초 사용자7장의 전후 위치

| 최초 캡처 | 개선 전 | 개선 후 |
|---|---|---|
| gateway·payments | 8장 | 9~10장 |
| payments CPU | 17장 | 18장 |
| web·auth | 15장 | 16장 |
| payments·cache | 5장 | 6~7장 |
| 로그인·대상 없음 | 13장 | 14장 |
| billing 미등록 | 11장 | 12장 |
| 이름 기억 | 19장 | 20장 |

## 화면과 연결 기록

| 장 | 내용 | 실제 화면 | 연결 근거 |
|---|---|---|---|
| 5 | 개선 1 전 · cache를 조회하지 않고 원인을 추정했다 | [원본 캡처](../day1/evidence/user-screenshots/04-payments-cache.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 6 | 개선 1 후 · 두 서비스를 각각 조사했다 1/2 | [원본 캡처](../day2/evidence/review-q06-first.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/research.py) · [기록4](../all_total_vue_student/agent/nodes.py) |
| 7 | 개선 1 후 · 공통 원인은 미확인으로 남겼다 2/2 | [원본 캡처](../day2/evidence/review-q06-second.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 8 | 개선 1 전 · gateway만 조회했다 | [원본 캡처](../day1/evidence/user-screenshots/01-gateway-payments.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 9 | 개선 1 후 · 요청을 주고받는 두 서비스를 조회했다 | [원본 캡처](../day2/evidence/review-q04-first.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 10 | 개선 1 후 · 두 서비스의 결과와 근거를 제시했다 | [원본 캡처](../day2/evidence/review-q04-second.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 11 | 개선 2 전 · billing을 묻자 auth를 조회했다 | [원본 캡처](../day1/evidence/user-screenshots/06-billing.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 12 | 개선 2 후 · 미등록이면 등록 이름을 다시 묻는다 | [원본 캡처](../day2/evidence/context-unknown-frame.jpg) | [기록1](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/evidence.py) |
| 13 | 개선 2 전 · 로그인만으로 auth를 조회했다 | [원본 캡처](../day1/evidence/user-screenshots/05-login.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 14 | 개선 2 후 · 서비스 이름을 먼저 확인한다 | [원본 캡처](../day2/evidence/review-q07-answer.jpg) | [기록1](../day2/results/contextual-captures/f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/nodes.py) |
| 15 | 개선 3 전 · 정상 web에 DB 장애 절차를 연결했다 | [원본 캡처](../day1/evidence/user-screenshots/03-web-auth.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 16 | 개선 3 후 · 정상·장애를 서비스별로 구분했다 | [원본 캡처](../day2/evidence/context-healthy-answer.jpg) | [기록1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) · [기록2](../all_total_vue_student/agent/evidence.py) · [기록3](../all_total_vue_student/agent/research.py) |
| 17 | 개선 4 전 · 로그 미수집인데 분석 결과처럼 답했다 | [원본 캡처](../day1/evidence/user-screenshots/02-payments-cpu.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 18 | 개선 4 후 · 조회 결과과 매뉴얼 원문으로 보고했다 | [원본 캡처](../day2/evidence/review-q01-answer.jpg) | [기록1](../day2/results/contextual-captures/3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json) · [기록2](../all_total_vue_student/agent/reporting.py) · [기록3](../all_total_vue_student/agent/validation.py) · [기록4](../all_total_vue_student/agent/evidence.py) |
| 19 | 대화 개선 전 · 사용자 이름을 자기소개에 섞었다 | [원본 캡처](../day1/evidence/user-screenshots/07-name-recall.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 20 | 대화 개선 후 · 사용자 이름을 올바르게 답한다 | [원본 캡처](../day2/evidence/review-q10-answer.jpg) | [기록1](../day2/results/contextual-captures/review-suite.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/session_store.py) |
| 21 | 개선 5 전 · 시간 초과 뒤 안내가 없었다 | [원본 캡처](../day2/evidence/before-main-viewport.jpg) | [기록1](../day2/evidence/ui-capture-context.json) |
| 22 | 개선 5 후 · 시간 제한을 알리고 근거를 보존했다 1/2 | [원본 캡처](../day2/evidence/story-timeout-first.jpg) | [기록1](../day2/results/story-timeout/timeout.json) · [기록2](../all_total_vue_student/server.py) · [기록3](../all_total_vue_student/agent/nodes.py) |
| 23 | 개선 5 후 · 두 서비스의 조회 결과을 남겼다 2/2 | [원본 캡처](../day2/evidence/story-timeout-second.jpg) | [기록1](../day2/results/story-timeout/timeout.json) |
| 24 | 추가 1 · 증상에 맞는 매뉴얼을 검색한다 | [원본 캡처](../day2/evidence/review-q03-answer.jpg) | [기록1](../all_total_vue_student/agent/retrieval.py) · [기록2](../all_total_vue_student/agent/research.py) · [기록3](../all_total_vue_student/mcp_server.py) · [기록4](../day2/results/contextual-captures/cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json) · [기록5](../all_total_vue_student/agent/deps.py) |
| 25 | 추가 2 · 답변에 사용한 근거를 화면에 표시한다 | [원본 캡처](../day2/evidence/context-healthy-evidence.jpg) | [기록1](../all_total_vue_student/agent/evidence.py) · [기록2](../all_total_vue_student/server.py) · [기록3](../all_total_vue_student/web_chat.html) · [기록4](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 26 | 추가 3 · 같은 질문의 결과를 자동 비교한다 | [원본 캡처](../day2/evidence/evaluation-cases.jpg) | [기록1](../day2/scripts/build_evaluation_evidence.py) · [기록2](../day1/results/baseline-ollama/results.json) · [기록3](../day2/results/improved-ollama/results.json) · [기록4](../day2/tests/unit-tests-story.txt) · [기록5](../all_total_vue_student/tests/test_core.py) |
| 28 | 실제 측정 기록과 판정 기준 | [원본 캡처](../day2/evidence/evaluation-criteria.jpg) | [기록1](../day2/scripts/build_evaluation_evidence.py) · [기록2](../day1/evaluation/cases.json) · [기록3](../day1/scripts/run_baseline.py) · [기록4](../day2/results/comparison/summary.json) · [기록5](../day1/results/baseline-ollama/results.json) · [기록6](../day2/results/improved-ollama/results.json) |

## 그래프

27장은 [전후 원시 기록](../day2/results/comparison/presentation-metrics.json)에서 만든 편집 가능한 막대그래프4개다. [집계 코드](../day2/scripts/build_presentation_metrics.py)가 필요한 서비스 수집17/20·20/20, 조회 범위15/20·20/20, 문서11/12·12/12와 같은16문항 시간 중앙값을 계산한다. 그래프의 시간은 소수 둘째 자리로 표시한다.28장의 실제 보고서 캡처와 같은 기록을 사용하며 새 모델 평가 결과를 추가하지 않았다.

PPT의 실제 캡처23개는 원본 바이트 그대로다. 그래프를 실제 대화 화면으로 제시하지 않는다. 출처 경로와 상세 코드 이름은 이 문서·구현 노트에 유지한다.

[전체 회귀·원시 실행 기록](../day2/results/contextual-captures/SUMMARY.md)
