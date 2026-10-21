# 발표 화면과 원시 기록

현재 발표자료는 [질문·응답 보존판](../output/presentation/incident-diagnosis-agent-context.pptx)이다. PPT의 사진 10장은 캡처 파일 바이트와 일치하며 이미지 자르기를 적용하지 않았다. viewport는 해당 시점의 실제 화면이고 전체 페이지 캡처도 별도 보존했다.

| PPT | 실제 입력·화면 종류 | 캡처 원본 | 연결 기록 |
|---|---|---|---|
| 3 | web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘 / 원본 앱 최종 답변 | [원본](../day2/evidence/before-healthy-answer-revision.jpg) | [원본 프롬프트](../day2/evidence/before-healthy-prompt-revision.jpg) |
| 4~5 | 같은 질문 / 개선 앱의 전체 최종 답변과 근거를 연속 화면으로 표시 | [답변](../day2/evidence/context-healthy-answer.jpg) · [근거](../day2/evidence/context-healthy-evidence.jpg) | [실제 이벤트·모델 원문](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| 7 | billing-service 응답이 느려요 / 미등록 확인 요청 | [화면](../day2/evidence/context-unknown-frame.jpg) · [전체](../day2/evidence/context-unknown-full.jpg) | [보고 LLM 호출 0회](../day2/results/contextual-captures/55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |
| 10 | web-01·auth 질문 / 실제 LLM 원문 파일 화면, 앱 UI 아님 | [파일 화면](../day2/evidence/context-llm-raw.jpg) | [원문 포함 JSON](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) · [파생 TXT](../day2/results/contextual-captures/LLM_RAW.txt) |
| 11 | cache-service 메모리 사용률이 높아요. 지금 재시작해야 하나요? / 실제 질문·전체 답변 | [화면](../day2/evidence/context-cache-answer.jpg) · [전체](../day2/evidence/context-cache-full.jpg) | [실제 이벤트·모델 원문](../day2/results/contextual-captures/896fa769-6cf9-4c0a-8a16-450c703d2020-7e899df7.json) |
| 12 | web-01 상태를 확인해줘 / degraded·알림 없음의 제어 시험 | [전체](../day2/evidence/after-insufficient-controlled.jpg) | [제어 조건·원시 이벤트](../day2/results/presentation-scenarios/SUMMARY.md) |
| 13 | payments-service 응답이 느려요 / 요청 상한 8초의 제어 시험 | [전체](../day2/evidence/after-timeout-controlled.jpg) | [기본 상한 60초와 구분](../day2/results/presentation-scenarios/SUMMARY.md) |
| 14 | 20건 측정 결과의 보고서 화면, 앱 UI 아님 | [보고서 화면](../day2/evidence/comparison.jpg) | [측정 결과와 분모](../day2/results/comparison/REPORT.md) |
| 15 | 본편 4~5장과 같은 실행의 질문·답변·근거·완료 상태 전체 | [전체 페이지](../day2/evidence/context-healthy-full.jpg) | [실제 이벤트](../day2/results/contextual-captures/49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |

질문·답변 문구를 이미지에 덧씌우거나 일부 문장만 추출해 앱 화면처럼 만들지 않았다. 파일 화면과 결과 보고서는 캡처 자체는 실제 브라우저 화면이지만 앱 대화의 증거로 대신 쓰지 않는다. 긴 전체 원본은 투사 시 글씨가 작아지므로 본편 연속 화면을 읽고 원본은 확대 검토에 사용한다.

LLM은 구조화 JSON으로 서비스·수치·문서·절차 번호를 선택한다. 검증 후 코드가 최종 보고서를 구성한다. 미등록·정보 부족·시간 초과 안내를 검증된 모델 작성 성공으로 표현하지 않는다.
