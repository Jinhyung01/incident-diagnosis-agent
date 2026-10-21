# 발표 화면과 원시 기록

현재 발표자료는 [질문·응답 보존판](../output/presentation/incident-diagnosis-agent-review.pptx)이다. PPT의 사진 20장은 캡처 파일 바이트와 일치하며 이미지 자르기를 적용하지 않았다. viewport는 해당 시점의 실제 화면이고 전체 페이지 캡처도 별도 보존했다.

| PPT | 실제 입력·화면 종류 | 캡처 원본 | 연결 기록 |
|---|---|---|---|
| 3 | web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘 / 원본 앱 최종 답변 | [원본](../day2/evidence/before-healthy-answer-revision.jpg) | [원본 프롬프트](../day2/evidence/before-healthy-prompt-revision.jpg) |
| 4~5 | 같은 질문 / 개선 앱의 전체 최종 답변과 근거를 연속 화면으로 표시 | [답변](../day2/evidence/context-healthy-answer.jpg) · [근거](../day2/evidence/context-healthy-evidence.jpg) | [실제 이벤트·모델 원문](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 7 | billing-service 응답이 느려요 / 미등록 확인 요청 | [화면](../day2/evidence/context-unknown-frame.jpg) · [전체](../day2/evidence/context-unknown-full.jpg) | [보고 LLM 호출 0회](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |
| 10 | web-01·auth 질문 / 실제 LLM 원문 파일 화면, 앱 UI 아님 | [파일 화면](../day2/evidence/context-llm-raw.jpg) | [원문 포함 JSON](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) · [파생 TXT](../day2/results/contextual-captures/LLM_RAW.txt) |
| 11 | cache-service 메모리 사용률이 계속 올라가고 있어요 / 원래 Q02의 실제 질문·전체 답변 | [화면](../day2/evidence/review-q02-answer.jpg) · [전체](../day2/evidence/review-q02-full.jpg) | [Q02 기록](../day2/results/contextual-captures/271a4d39-90ec-4732-b7ea-a1515663f5c3-c915a919.json) |
| 12 | web-01 상태를 확인해줘 / degraded·알림 없음의 제어 시험 | [전체](../day2/evidence/after-insufficient-controlled.jpg) | [제어 조건·원시 이벤트](../day2/results/presentation-scenarios/SUMMARY.md) |
| 13 | payments-service 응답이 느려요 / 요청 상한 8초의 제어 시험 | [전체](../day2/evidence/after-timeout-controlled.jpg) | [기본 상한 60초와 구분](../day2/results/presentation-scenarios/SUMMARY.md) |
| 14 | 20건 측정 결과의 보고서 화면, 앱 UI 아님 | [보고서 화면](../day2/evidence/comparison.jpg) | [측정 결과와 분모](../day2/results/comparison/REPORT.md) |
| 15 | 본편 4~5장과 같은 실행의 질문·답변·근거·완료 상태 전체 | [전체 페이지](../day2/evidence/context-healthy-full.jpg) | [실제 이벤트](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |

질문·답변 문구를 이미지에 덧씌우거나 일부 문장만 추출해 앱 화면처럼 만들지 않았다. 파일 화면과 결과 보고서는 캡처 자체는 실제 브라우저 화면이지만 앱 대화의 증거로 대신 쓰지 않는다. 긴 전체 원본은 투사 시 글씨가 작아지므로 본편 연속 화면을 읽고 원본은 확대 검토에 사용한다.

LLM은 구조화 JSON으로 서비스·수치·문서·절차 번호를 선택한다. 검증 후 코드가 최종 보고서를 구성한다. 미등록·정보 부족·시간 초과 안내를 검증된 모델 작성 성공으로 표현하지 않는다.

## 수업의 원래 10개 시나리오

원래 회귀 문서의 정확한 질문과 목적에 연결했다. 원본의 Q07·Q08 auth 기본 처리는 의도된 정책이며, 개선 버전은 대상 확인 안내로 바꿨다. Q09 인사·Q10 이름은 코드 응답 경로다. Q05·Q08은 직전 실제 완료 캡처를 재사용했고 나머지는 이번 검토에서 보강했다.

| ID | 정확한 질문 | 확인한 결과 | 실제 캡처 | 원시 기록 |
|---|---|---|---|---|
| Q01 | payments-service 결제 응답이 느려지고 CPU가 치솟았어요, 원인 확인해주세요 | payments 확인·CPU 문서 연결 | [화면1](../day2/evidence/review-q01-answer.jpg) | [기록1](../day2/results/contextual-captures/3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json) |
| Q02 | cache-service 메모리 사용률이 계속 올라가고 있어요 | cache 확인·메모리 문서 연결 | [화면1](../day2/evidence/review-q02-answer.jpg) | [기록1](../day2/results/contextual-captures/271a4d39-90ec-4732-b7ea-a1515663f5c3-c915a919.json) |
| Q03 | log-service 디스크 공간이 부족하다는 알림이 왔어요 | log 확인·디스크 문서 연결 | [화면1](../day2/evidence/review-q03-answer.jpg) | [기록1](../day2/results/contextual-captures/cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json) |
| Q04 | gateway-service에서 payments-service로 가는 요청이 타임아웃 나고 있어요 | gateway·payments 각각 조사 | [화면1](../day2/evidence/review-q04-first.jpg) · [화면2](../day2/evidence/review-q04-second.jpg) | [기록1](../day2/results/contextual-captures/f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json) |
| Q05 | web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘 | web 정상·auth 지연 문서 분리 | [화면1](../day2/evidence/context-healthy-answer.jpg) · [화면2](../day2/evidence/context-healthy-evidence.jpg) | [기록1](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| Q06 | payments-service랑 cache-service 둘 다 저하됐는데 공통 원인이 있는지 분석해줘 | 두 서비스 조사·공통 원인 미확정 | [화면1](../day2/evidence/review-q06-first.jpg) · [화면2](../day2/evidence/review-q06-second.jpg) | [기록1](../day2/results/contextual-captures/a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json) |
| Q07 | 로그인 응답이 느려요, 원인 확인해주세요 | 서비스 이름 확인 요청 | [화면1](../day2/evidence/review-q07-answer.jpg) | [기록1](../day2/results/contextual-captures/f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json) |
| Q08 | billing-service 응답이 느려요 | 미등록 안내·임의 대체 생략 | [화면1](../day2/evidence/context-unknown-frame.jpg) | [기록1](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |
| Q09 | 안녕, 너는 누구야? | 일반 대화·모니터링 생략 | [화면1](../day2/evidence/review-q09-answer.jpg) | [기록1](../day2/results/contextual-captures/d3cb38b5-ab56-4a84-a720-56ef5e09bf11-1c41cc9f.json) |
| Q10 | 제 이름은 민수입니다 → 제 이름이 뭐였죠? | 재시작 뒤 사용자 이름 유지 | [화면1](../day2/evidence/review-q10-before-restart.jpg) · [화면2](../day2/evidence/review-q10-answer.jpg) | [기록1](../day2/results/contextual-captures/a32674df-835a-4ed8-889d-49281a8c9b81-db829e26.json) · [기록2](../day2/results/contextual-captures/a32674df-835a-4ed8-889d-49281a8c9b81-a7e8818f.json) |

[시나리오 대응·재시작 제어 기록 JSON](../day2/results/contextual-captures/review-suite.json). Q10의 이름 선언·재질문은 같은 thread이고 서버 PID는24787→25021이다. 재시작은 화면만으로 입증하지 않으며 실제 프로세스 종료·새 시작의 도구 출력과 이 제어 기록을 함께 사용한다. 전체 페이지 원본은 `review-q01/02/03/04/06/07/09-full.jpg`, `review-q10-after-restart.jpg`로 보존했다. Q05 전체는 `context-healthy-full.jpg`, Q08 전체는 `context-unknown-full.jpg`다.
