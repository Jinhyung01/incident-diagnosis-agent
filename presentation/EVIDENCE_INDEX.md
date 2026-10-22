# 질문·응답과 구현의 증빙

현재 자료는 [발표 본문](../output/presentation/incident-diagnosis-agent-code-proof.pptx)이다. 최초 PNG7개와 같은 질문의 개선 응답을 본문에 유지한다. 코드 캡처4개는 실제 소스의 발췌이며 파일명·줄 번호와 강조 줄을 표시한다.

| 장 | 내용 | 실제 화면·코드 | 연결 기록 |
|---|---|---|---|
| 4 | 개선 1 전: cache 조회 없이 공통 원인을 추정 | [캡처](../day1/evidence/user-screenshots/04-payments-cache.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 5 | 개선 1 구현: 요청한 서비스마다 조회 작업 구성 | [캡처](../day2/evidence/code/01-target-tasks.png) | [기록1](../all_total_vue_student/agent/targets.py) · [기록2](../day2/evidence/code/MANIFEST.json) |
| 6 | 개선 1 후: 요청한 서비스로 조회 목록을 구성 | [캡처](../day2/evidence/review-q06-first.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/research.py) · [기록4](../all_total_vue_student/agent/nodes.py) |
| 7 | 개선 1 후: 공통 원인은 미확인으로 표시 | [캡처](../day2/evidence/review-q06-second.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 8 | 개선 1 전: gateway만 조회 | [캡처](../day1/evidence/user-screenshots/01-gateway-payments.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 9 | 개선 1 후: 요청을 주고받는 양쪽을 조사 | [캡처](../day2/evidence/review-q04-first.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 10 | 개선 1 후: 두 서비스의 결과와 근거를 함께 제시 | [캡처](../day2/evidence/review-q04-second.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 11 | 개선 2 전: billing을 물었는데 auth를 조회 | [캡처](../day1/evidence/user-screenshots/06-billing.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 12 | 개선 2 구현: 조사 대상이 없으면 이름 확인 | [캡처](../day2/evidence/code/02-confirm-target.png) | [기록1](../all_total_vue_student/agent/evidence.py) · [기록2](../day2/evidence/code/MANIFEST.json) |
| 13 | 개선 2 후: 미등록 서비스는 이름부터 확인 | [캡처](../day2/evidence/context-unknown-frame.jpg) | [기록1](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/evidence.py) |
| 14 | 개선 2 전: 서비스 이름 없이 auth를 조회 | [캡처](../day1/evidence/user-screenshots/05-login.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 15 | 개선 2 후: 서비스 이름을 먼저 확인 | [캡처](../day2/evidence/review-q07-answer.jpg) | [기록1](../day2/results/contextual-captures/f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/nodes.py) |
| 16 | 개선 3 전: 정상인 web에 DB 장애 매뉴얼 연결 | [캡처](../day1/evidence/user-screenshots/03-web-auth.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 17 | 개선 3 구현: 장애 조사 대상만 매뉴얼 검색 | [캡처](../day2/evidence/code/03-skip-runbook.png) | [기록1](../all_total_vue_student/agent/research.py) · [기록2](../day2/evidence/code/MANIFEST.json) |
| 18 | 개선 3 후: 서비스별 상태에 맞는 매뉴얼 선택 | [캡처](../day2/evidence/context-healthy-answer.jpg) | [기록1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) · [기록2](../all_total_vue_student/agent/evidence.py) · [기록3](../all_total_vue_student/agent/research.py) |
| 19 | 개선 4 전: 조회하지 않은 로그를 분석한 것처럼 답변 | [캡처](../day1/evidence/user-screenshots/02-payments-cpu.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 20 | 개선 4 구현: 관측값 불일치와 원인 확정 검사 | [캡처](../day2/evidence/code/04-evidence-check.png) | [기록1](../all_total_vue_student/agent/validation.py) · [기록2](../day2/evidence/code/MANIFEST.json) |
| 21 | 개선 4 후: 수치와 절차를 검증한 뒤 답변 | [캡처](../day2/evidence/review-q01-answer.jpg) | [기록1](../day2/results/contextual-captures/3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json) · [기록2](../all_total_vue_student/agent/reporting.py) · [기록3](../all_total_vue_student/agent/validation.py) · [기록4](../all_total_vue_student/agent/evidence.py) |
| 22 | 대화 개선 전: 사용자 이름을 자기소개에 사용 | [캡처](../day1/evidence/user-screenshots/07-name-recall.png) | [기록1](../day1/evidence/OBSERVATIONS.md) |
| 23 | 대화 개선 후: 사용자가 밝힌 이름으로 답변 | [캡처](../day2/evidence/review-q10-answer.jpg) | [기록1](../day2/results/contextual-captures/review-suite.json) · [기록2](../all_total_vue_student/agent/targets.py) · [기록3](../all_total_vue_student/agent/session_store.py) |
| 25 | 추가 1: 증상에 맞는 매뉴얼을 RAG로 검색 | [캡처](../day2/evidence/review-q03-answer.jpg) | [기록1](../all_total_vue_student/agent/retrieval.py) · [기록2](../all_total_vue_student/agent/research.py) · [기록3](../all_total_vue_student/mcp_server.py) · [기록4](../day2/results/contextual-captures/cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json) · [기록5](../all_total_vue_student/agent/deps.py) |
| 26 | 추가 2: 답변에 사용한 근거를 함께 표시 | [캡처](../day2/evidence/context-healthy-evidence.jpg) | [기록1](../all_total_vue_student/agent/evidence.py) · [기록2](../all_total_vue_student/server.py) · [기록3](../all_total_vue_student/web_chat.html) · [기록4](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 27 | 추가 3: 같은 질문으로 전후 결과를 자동 비교 | [캡처](../day2/evidence/evaluation-cases.jpg) | [기록1](../day2/scripts/build_evaluation_evidence.py) · [기록2](../day1/results/baseline-ollama/results.json) · [기록3](../day2/results/improved-ollama/results.json) · [기록4](../day2/tests/unit-tests-story.txt) · [기록5](../all_total_vue_student/tests/test_core.py) |

코드 캡처는 실제 Python 파일의 지정된 줄을 변경 없이 발췌해 브라우저에서 렌더링한 화면이다. IDE 화면으로 표현하지 않는다. [파일 해시·줄 범위·발췌 원문](../day2/evidence/code/MANIFEST.json)으로 실제 코드와 대조할 수 있다.

28장은 [보존한40개 실행의 파생 집계](../day2/results/comparison/presentation-metrics.json)를 편집 가능한 그래프로 표시한다. 세 선택 기준의 비율과 원시 건수를 함께 제시하고, 같은16문항의 시간은 보조로 표시한다.

사용자가 응답 전에 직접 종료했던 진행 캡처는 장애 증거에서 제외했다. 삭제한 개선5나 별도 지연 주입 시험을 현재 발표에 포함하지 않는다.
