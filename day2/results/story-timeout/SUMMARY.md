# 같은 질문의 실패 처리와 평가 기능 시연

2026-10-22 실제 MCP·그래프·SSE·UI 실행이다. 질문은 최초 사용자 캡처 및 별도 원본 실패 재현과 같은 `payments-service랑 cache-service 둘 다 저하됐는데 공통 원인이 있는지 분석해줘`다.

보고 생성 의존성에30초 지연을 주고 시험 요청 상한을8초로 낮췄다. 기본은 전체60초·호출25초다. 실제8.004초에 시간 제한 안내를 반환하고 payments CPU91%·메모리55%, cache CPU42%·메모리89%와 문서 원문을 보존했다. 검증된 모델 보고 성공이 아닌 코드 제한 안내다. 일반 성능이나 기존20건 통계에 합산하지 않는다.

[원시 이벤트](timeout.json) · [fixture](monitoring-fixture.json) · [전체 UI](../../evidence/story-timeout-full.jpg) · [연속1](../../evidence/story-timeout-first.jpg) · [연속2](../../evidence/story-timeout-second.jpg)

기존 기록을 덮어쓰지 않도록 `serve_presentation_scenarios.py --output day2/results/story-timeout`을 사용했다. 재현은 비어 있는 새 출력 폴더를 지정하고 백엔드·프록시 양쪽에 같은 경로를 준다.

추가 기능인 비교 집계기는 보존된 원시 결과에서 보고서를 다시 생성했다. 기존 summary.json 해시가 유지됐고 LLM20건을 다시 실행한 것은 아니다. [집계 실행 기록](comparison-regeneration.txt) · [실제 보고서 캡처](../../evidence/story-evaluation-report.jpg)
