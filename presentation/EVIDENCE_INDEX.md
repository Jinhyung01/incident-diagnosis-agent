# 질문·응답과 개선 결과의 증빙

현재 발표자료는 [발표 본문](../output/presentation/incident-diagnosis-agent-ready.pptx)이다. 최초 사용자 PNG 7개를 모두 본문에 원본 그대로 넣었다. 최초 관측과 고정 재실행의 수치는 다른 시점이며 성능 비교는 별도 20건 측정으로 구분한다.

## 최초 사용자 7장의 전후 위치

| 최초 캡처 | 개선 전 | 개선 후 |
|---|---|---|
| gateway→payments | 6장 | 7~8장 |
| payments CPU | 15장 | 16장 |
| web·auth | 13장 | 14장 |
| payments·cache | 3장 | 4~5장 |
| 로그인·대상 없음 | 11장 | 12장 |
| billing 미등록 | 9장 | 10장 |
| 이름 기억 | 17장 | 18장 |

## 슬라이드별 화면·출처

| PPT | 내용 | 원본 파일 | 연결 기록 |
|---|---|---|---|
| 3 | 개선 1 전 · cache를 조회하지 않고 원인을 추정했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/04-payments-cache.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 4 | 개선 1 후 · 두 서비스를 각각 조사했다 1/2 | [수정하지 않은 캡처](../day2/evidence/review-q06-first.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 5 | 개선 1 후 · 공통 원인은 미확인으로 남겼다 2/2 | [수정하지 않은 캡처](../day2/evidence/review-q06-second.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 6 | 개선 1 전 · gateway만 조회했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/01-gateway-payments.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 7 | 개선 1 후 · 요청을 주고받는 두 서비스를 조회했다 | [수정하지 않은 캡처](../day2/evidence/review-q04-first.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 8 | 개선 1 후 · 두 서비스의 결과와 근거를 제시했다 | [수정하지 않은 캡처](../day2/evidence/review-q04-second.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 9 | 개선 2 전 · billing을 묻자 auth를 조회했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/06-billing.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 10 | 개선 2 후 · 미등록이면 등록 이름을 다시 묻는다 | [수정하지 않은 캡처](../day2/evidence/context-unknown-frame.jpg) | [기록1](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |
| 11 | 개선 2 전 · 로그인만으로 auth를 조회했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/05-login.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 12 | 개선 2 후 · 서비스 이름을 먼저 확인한다 | [수정하지 않은 캡처](../day2/evidence/review-q07-answer.jpg) | [기록1](../day2/results/contextual-captures/f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json) |
| 13 | 개선 3 전 · 정상 web에 DB 장애 절차를 연결했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/03-web-auth.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 14 | 개선 3 후 · 정상·장애를 서비스별로 구분했다 | [수정하지 않은 캡처](../day2/evidence/context-healthy-answer.jpg) | [기록1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 15 | 개선 4 전 · 로그 미수집인데 분석 결과처럼 답했다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/02-payments-cpu.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 16 | 개선 4 후 · 관측과 매뉴얼 원문으로 보고했다 | [수정하지 않은 캡처](../day2/evidence/review-q01-answer.jpg) | [기록1](../day2/results/contextual-captures/3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json) |
| 17 | 대화 개선 전 · 사용자 이름을 자기소개에 섞었다 | [수정하지 않은 캡처](../day1/evidence/user-screenshots/07-name-recall.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 18 | 대화 개선 후 · 사용자 이름을 올바르게 답한다 | [수정하지 않은 캡처](../day2/evidence/review-q10-answer.jpg) | [기록1](../day2/results/contextual-captures/review-suite.json) |
| 19 | 개선 5 전 · 시간 초과 뒤 안내가 없었다 | [수정하지 않은 캡처](../day2/evidence/before-main-viewport.jpg) | [기록1](../day2/evidence/ui-capture-context.json) |
| 20 | 개선 5 후 · 시간 제한을 알리고 근거를 보존했다 1/2 | [수정하지 않은 캡처](../day2/evidence/story-timeout-first.jpg) | [기록1](../day2/results/story-timeout/timeout.json) · [기록2](../all_total_vue_student/server.py) · [기록3](../all_total_vue_student/agent/nodes.py) |
| 21 | 개선 5 후 · 두 서비스의 관측을 남겼다 2/2 | [수정하지 않은 캡처](../day2/evidence/story-timeout-second.jpg) | [기록1](../day2/results/story-timeout/timeout.json) |
| 22 | 추가 1 · 증상에 맞는 매뉴얼을 검색한다 | [수정하지 않은 캡처](../day2/evidence/review-q03-answer.jpg) | [기록1](../all_total_vue_student/agent/retrieval.py) · [기록2](../all_total_vue_student/agent/research.py) · [기록3](../all_total_vue_student/mcp_server.py) · [기록4](../day2/results/contextual-captures/cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json) |
| 23 | 추가 2 · 답변에 사용한 근거를 화면에 표시한다 | [수정하지 않은 캡처](../day2/evidence/context-healthy-evidence.jpg) | [기록1](../all_total_vue_student/agent/evidence.py) · [기록2](../all_total_vue_student/server.py) · [기록3](../all_total_vue_student/web_chat.html) · [기록4](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |

| 24 | 추가 3 · 같은 질문의 결과를 자동 비교한다 | [실제 평가 보고서 화면](../day2/evidence/evaluation-cases.jpg) | [집계 코드](../day2/scripts/build_evaluation_evidence.py) · [전 실행](../day1/results/baseline-ollama/results.json) · [후 실행](../day2/results/improved-ollama/results.json) |
| 25 | 측정 기준과 전후 결과 | [실제 평가 보고서 화면](../day2/evidence/evaluation-criteria.jpg) | [집계 코드](../day2/scripts/build_evaluation_evidence.py) · [전 실행](../day1/results/baseline-ollama/results.json) · [후 실행](../day2/results/improved-ollama/results.json) |
PPT는 서로 다른 캡처 파일 23개를 포함한다. 이미지 바이트를 원본과 대조하며 자르기·답변 덮기를 적용하지 않는다. 사진 밖의 문제 해석과 구현 설명은 편집 가능한 텍스트다. 긴 답변은 같은 요청의 연속 viewport로 제시한다.

그 밖의 회귀 질문과 원시 실행 기록은 [전체 검증 기록](../day2/results/contextual-captures/SUMMARY.md)에 유지한다. PPT에 중복 캡처·질문 위치 목록을 덧붙이지 않는다.
슬라이드에 날짜·사용자 최초 실행·원본 재현 등의 제작 설명을 넣지 않는다. 출처는 이 문서와 발표자 노트로 추적한다. 측정 기준과 결과 화면은 원시 JSON에서 보고서를 생성한 실제 브라우저 캡처이며 새 모델 실행 결과를 추가한 것이 아니다.
