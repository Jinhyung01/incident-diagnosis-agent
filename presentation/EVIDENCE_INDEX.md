# 최초 사진·같은 질문의 개선·추가 기능 증빙

현재 발표자료는 [사례별 전후 설명판](../output/presentation/incident-diagnosis-agent-presentation.pptx)이다. 최초 사용자7개 PNG를 모두 원본 그대로 넣었다. 최초 관측과 고정 재실행 수치는 다른 시점이며, 성능 비교는 별도20건 측정으로 구분한다.

## 최초 사용자7장의 전후 위치

| 최초 캡처 | 개선 전 | 개선 후 |
|---|---|---|
| gateway→payments | 21장 | 22~23장 |
| payments CPU | 10장 | 11장 |
| web·auth | 8장 | 9장 |
| payments·cache | 3장 | 4~5장 |
| 로그인·대상 없음 | 24장 | 25장 |
| billing 미등록 | 6장 | 7장 |
| 이름 기억 | 26장 | 27장 |

## 슬라이드별 화면·출처

| PPT | 화면 종류·실제 자료 | 원본 파일 | 연결 기록 |
|---|---|---|---|
| 3 | 사용자2026-10-20 최초 실행 / 개선 1 전 · cache를 조회하지 않고 원인을 추정했다 | [전체 원본](../day1/evidence/user-screenshots/04-payments-cache.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 4 | 실제 개선 UI / 개선 1 후 · 두 서비스를 각각 조사했다 1/2 | [전체 원본](../day2/evidence/review-q06-first.jpg) | [근거1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 5 | 실제 개선 UI / 개선 1 후 · 공통 원인은 미확인으로 남겼다 2/2 | [전체 원본](../day2/evidence/review-q06-second.jpg) | [근거1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| 6 | 사용자2026-10-20 최초 실행 / 개선 2 전 · billing을 묻자 auth를 조회했다 | [전체 원본](../day1/evidence/user-screenshots/06-billing.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 7 | 실제 개선 UI / 개선 2 후 · 미등록이면 등록 이름을 다시 묻는다 | [전체 원본](../day2/evidence/context-unknown-frame.jpg) | [근거1](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |
| 8 | 사용자2026-10-20 최초 실행 / 개선 3 전 · 정상 web에 DB 장애 절차를 연결했다 | [전체 원본](../day1/evidence/user-screenshots/03-web-auth.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 9 | 실제 개선 UI / 개선 3 후 · 정상·장애를 서비스별로 구분했다 | [전체 원본](../day2/evidence/context-healthy-answer.jpg) | [근거1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 10 | 사용자2026-10-20 최초 실행 / 개선 4 전 · 로그 미수집인데 분석 결과처럼 답했다 | [전체 원본](../day1/evidence/user-screenshots/02-payments-cpu.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 11 | 실제 개선 UI / 개선 4 후 · 관측과 매뉴얼 원문으로 보고했다 | [전체 원본](../day2/evidence/review-q01-answer.jpg) | [근거1](../day2/results/contextual-captures/3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json) |
| 12 | 보존 원본의 별도 재실행 / 개선 5 전 · 추가 재현에서는 답변을 완료하지 못했다 | [전체 원본](../day2/evidence/before-main-viewport.jpg) | [근거1](../day2/evidence/ui-capture-context.json) · [근거2](../day2/evidence/ui-capture-context.json) |
| 13 | 지연 주입 제어 시험 / 개선 5 후 · 시간 제한을 알리고 근거를 보존했다 1/2 | [전체 원본](../day2/evidence/story-timeout-first.jpg) | [근거1](../day2/results/story-timeout/timeout.json) · [근거2](../all_total_vue_student/server.py) · [근거3](../all_total_vue_student/agent/nodes.py) |
| 14 | 지연 주입 제어 시험 / 개선 5 후 · 두 서비스의 관측을 남겼다 2/2 | [전체 원본](../day2/evidence/story-timeout-second.jpg) | [근거1](../day2/results/story-timeout/timeout.json) |
| 15 | 실제 개선 UI / 추가 1 · RAG로 대응 매뉴얼을 검색한다 | [전체 원본](../day2/evidence/review-q03-answer.jpg) | [근거1](../all_total_vue_student/agent/retrieval.py) · [근거2](../all_total_vue_student/agent/research.py) · [근거3](../all_total_vue_student/mcp_server.py) · [근거4](../day2/results/contextual-captures/cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json) |
| 16 | 실제 개선 UI / 추가 2 · 답변에 사용한 근거를 화면에 표시한다 | [전체 원본](../day2/evidence/context-healthy-evidence.jpg) | [근거1](../all_total_vue_student/agent/evidence.py) · [근거2](../all_total_vue_student/server.py) · [근거3](../all_total_vue_student/web_chat.html) · [근거4](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 17 | 실제 측정 결과 보고서 / 추가 3 · 회귀 테스트와 전후 비교를 재현한다 | [전체 원본](../day2/evidence/story-evaluation-report.jpg) | [근거1](../day2/evidence/comparison.jpg) · [근거2](../day1/scripts/run_baseline.py) · [근거3](../day2/scripts/build_comparison.py) · [근거4](../day2/results/comparison/summary.json) · [근거5](../day2/tests/unit-tests-story.txt) |
| 21 | 사용자2026-10-20 최초 실행 / 부록 · gateway만 조회한 최초 응답 | [전체 원본](../day1/evidence/user-screenshots/01-gateway-payments.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 22 | 실제 개선 UI / 부록 · 같은 gateway 질문의 개선 1/2 | [전체 원본](../day2/evidence/review-q04-first.jpg) | [근거1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 23 | 실제 개선 UI / 부록 · 같은 gateway 질문의 개선 2/2 | [전체 원본](../day2/evidence/review-q04-second.jpg) | [근거1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| 24 | 사용자2026-10-20 최초 실행 / 부록 · 로그인 질문을 auth로 가정한 최초 응답 | [전체 원본](../day1/evidence/user-screenshots/05-login.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 25 | 실제 개선 UI / 부록 · 같은 로그인 질문에 서비스 이름을 요청한다 | [전체 원본](../day2/evidence/review-q07-answer.jpg) | [근거1](../day2/results/contextual-captures/f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json) |
| 26 | 사용자2026-10-20 최초 실행 / 부록 · 사용자 이름을 자기소개에 섞은 최초 응답 | [전체 원본](../day1/evidence/user-screenshots/07-name-recall.png) | [근거1](../day1/evidence/OBSERVATIONS.md) |
| 27 | 실제 개선 UI / 부록 · 같은 두 턴에서 사용자 이름을 올바르게 답한다 | [전체 원본](../day2/evidence/review-q10-answer.jpg) | [근거1](../day2/results/contextual-captures/review-suite.json) |
| 28 | 보존 원본의 별도 재실행 / 부록 · 고정 지표로 다시 실행한 원본 web·auth | [전체 원본](../day2/evidence/before-healthy-answer-revision.jpg) | [근거1](../day2/evidence/ui-capture-context.json) |
| 29 | 실제 개선 UI / 부록 · 같은 고정 지표·질문의 개선 실행 | [전체 원본](../day2/evidence/context-healthy-answer.jpg) | [근거1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 30 | 실제 모델 원문 파일 화면·앱UI아님 / 부록 · 실제 보고 LLM은 JSON을 반환한다 | [전체 원본](../day2/evidence/context-llm-raw.jpg) | [근거1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 31 | 실제 개선 UI / 부록 · 정보가 부족하면 문서를 임의 선택하지 않는다 | [전체 원본](../day2/evidence/after-insufficient-controlled.jpg) | [근거1](../day2/results/presentation-scenarios/SUMMARY.md) |
| 32 | 실제 개선 UI / 부록 · 원래 Q02 메모리 상승 질문의 개선 응답 | [전체 원본](../day2/evidence/review-q02-answer.jpg) | [근거1](../day2/results/contextual-captures/271a4d39-90ec-4732-b7ea-a1515663f5c3-c915a919.json) |
| 33 | 실제 개선 UI / 부록 · 원래 Q09 일반 대화 경로 | [전체 원본](../day2/evidence/review-q09-answer.jpg) | [근거1](../day2/results/contextual-captures/d3cb38b5-ab56-4a84-a720-56ef5e09bf11-1c41cc9f.json) |
| 34 | 실제 측정 결과 보고서 / 부록 · 전후 측정 결과 보고서 원본 | [전체 원본](../day2/evidence/comparison.jpg) | [근거1](../day2/results/comparison/summary.json) |

PPT는 캡처 파일28개를 참조하며, 재집계한 보고서와 이전 보고서 캡처가 동일해 고유 이미지 바이트는27개다. 원본 파일과 PPT 내 이미지 바이트를 대조하며 자르기·답변 문구 덮기를 적용하지 않는다. 오른쪽의 문제 해석과 구현 설명은 사진과 분리한 편집 가능한 텍스트다.

긴 응답은 같은 요청의 연속 viewport와 전체 페이지 파일을 함께 보존한다. 시간 초과는 같은 payments·cache 질문에30초 생성 의존성 지연·8초 요청 상한을 준 제어 시험이다.8.004초에 제한 안내와 두 서비스 근거를 남겼다. 기본 상한60초·일반 성능과 구분한다.

RAG·근거 화면은 실제 개선 UI, 평가 기능은 실제 결과 JSON에서 만든 보고서 화면이다. 이름·인사·미등록·시간 초과 안내를 모델 작성 성공으로 표현하지 않는다.

[원래10개 시나리오의 원시 기록 대응](../day2/results/contextual-captures/review-suite.json) · [최초7장 해시](../day1/evidence/screenshot_inventory.json)
