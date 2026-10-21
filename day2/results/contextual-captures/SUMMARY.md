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
