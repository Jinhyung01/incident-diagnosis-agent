# 질문·답변을 함께 보존한 실제 UI 실행

2026-10-21. 기존 20건 비교와 별도인 발표 증빙용 실행이다. 실제 MCP·Ollama·그래프·SSE·UI를 사용했다. 모니터링 값은 원본 base 값에 jitter=0으로 고정했고 실제 조회 시각은 각 호출 시각이다. 답변을 미리 작성하거나 재생하지 않았다.

| 질문 | 모델 보고 호출 | 최종 상태 | 화면 표시 시간 | 원시 기록 |
|---|---:|---|---:|---|
| cache-service 메모리 사용률이 높아요. 지금 재시작해야 하나요? | 1 | validated | 7.767초 | [896fa769-6cf9-4c0a-8a16-450c703d2020-7e899df7.json](896fa769-6cf9-4c0a-8a16-450c703d2020-7e899df7.json) |
| web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘 | 1 | validated | 12.425초 | [49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json](49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json) |
| billing-service 응답이 느려요 | 0 | observation | 0.008초 | [55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json](55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json) |

`serve_capture_session.py`가 실제 보고 LLM의 반환값과 usage를 저장한 뒤 그대로 호출자에게 돌려준다. raw_model_output은 실제 모델 문자열이고 events의 FinalAnswer.reply는 검증·렌더링 후 사용자에게 보낸 최종 문장이다. 두 결과는 같은 의미의 파일로 취급하지 않는다.

`LLM_RAW.txt`와 UTF-8 BOM 사본은 web-01·auth 실행의 질문·모델 원문·원시 파일 해시를 보여주는 파생 텍스트 파일이다. 이 파일의 브라우저 캡처는 실제 앱 화면이 아니다. 원시 JSON과 대조할 수 있도록 보존했다.

미등록 billing 안내는 코드가 구성하며 보고 LLM을 호출하지 않았다. cache는 메모리 89%를 관측했고 90% 이상이라는 매뉴얼 조건을 원문으로 보존했다. 조건 충족 여부의 자동 판정·실제 조치는 지원하지 않는다.

긴 응답을 스크롤해도 질문이 보이도록 `.request`에 sticky CSS를 추가했다. 답변 데이터·문장을 편집하지 않았다. 전체 페이지와 연속 viewport 원본을 함께 보존한다.

캡처 관찰기는 순차 요청용이며 동시 요청 격리 성능을 검증하지 않았다. 최초 저장 이름의 thread 중복 문제를 발견해 요청별 UUID 접미사를 추가했다. 선택한 증빙은 완료된 최종 이벤트와 화면이 일치하는 요청이다. 기록은 덮어쓰지 않는다.

[캡처 목록](../../../presentation/EVIDENCE_INDEX.md) · [실행 래퍼](../../scripts/serve_capture_session.py)

## 전체 검토의 추가 UI 증빙

원래10개 시나리오를 실제 화면과 연결한 [대응 기록](review-suite.json)을 추가했다. Q05·Q08은 직전 완료 캡처를 재사용하고 나머지8개 시나리오의9개 요청을 이번 검토에서 실행했다. 이는 기존 통합검증10개·11요청이나20건 정량평가를 새로 측정한 숫자가 아니다.

- Q01: payments 확인·CPU 문서 연결. [3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json](3e26b7de-a591-4252-a03e-e3b7abfd824e-8df47df5.json)
- Q02: cache 확인·메모리 문서 연결. [271a4d39-90ec-4732-b7ea-a1515663f5c3-c915a919.json](271a4d39-90ec-4732-b7ea-a1515663f5c3-c915a919.json)
- Q03: log 확인·디스크 문서 연결. [cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json](cc4c77a5-5311-4797-9942-36ec51f66841-17dcde1e.json)
- Q04: gateway·payments 각각 조사. [f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json](f7d637e2-c911-417e-bf3f-3845fed685fa-33205f03.json)
- Q05: web 정상·auth 지연 문서 분리. [49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json](49ebc8c8-65fc-4aec-bc42-fd1829f048e9.json)
- Q06: 두 서비스 조사·공통 원인 미확정. [a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json](a19f84a4-7221-45f6-938e-f8dac295ea28-eca497a3.json)
- Q07: 서비스 이름 확인 요청. [f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json](f4e83364-7451-4377-a65d-6adaac6d4a8f-3fba43e9.json)
- Q08: 미등록 안내·임의 대체 생략. [55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json](55c381af-5efe-447d-9430-bf83a5b11c9d-c848919a.json)
- Q09: 일반 대화·모니터링 생략. [d3cb38b5-ab56-4a84-a720-56ef5e09bf11-1c41cc9f.json](d3cb38b5-ab56-4a84-a720-56ef5e09bf11-1c41cc9f.json)
- Q10: 재시작 뒤 사용자 이름 유지. [a32674df-835a-4ed8-889d-49281a8c9b81-db829e26.json](a32674df-835a-4ed8-889d-49281a8c9b81-db829e26.json) · [a32674df-835a-4ed8-889d-49281a8c9b81-a7e8818f.json](a32674df-835a-4ed8-889d-49281a8c9b81-a7e8818f.json)

이름 선언 뒤 캡처 서버를 정상 종료(PID24787)하고 같은DB로 시작(PID25021)한 후 같은thread에서 회상했다. 응답은 사용자님의 이름은 민수입니다였다. 브라우저의 두 턴과 실제 이벤트를 함께 보존했다. 코드가 사용자 역할의 저장 이력을 읽는 기능으로, LLM 장기 기억 성능으로 주장하지 않는다.
