# 사례별 구현과 실행 증빙

원래 질문을 실행한 화면과 같은 질문의 개선 결과를 연결했다. 모의 지표의 CPU·메모리 값은 실행 시점에 따라 바뀔 수 있어 그 차이를 개선 성과로 계산하지 않는다. 정량 비교는 같은 질문과 고정 지표로 실행한 기록을 사용한다.

## 개선 사항

| 항목 | 실제 동작을 바꾼 코드 | 개선 전 | 개선 후 |
|---|---|---|---|
| payments·cache 조사 누락 | [대상별 작업 구성](../all_total_vue_student/agent/targets.py) | [원래 질문·답변](evidence/before/04-payments-cache.png) | [두 서비스 조회](evidence/after/review-q06-first.jpg), [서비스별 결과](evidence/after/review-q06-second.jpg) |
| gateway·payments 조사 누락 | 같은 대상 추출·작업 구성 사용 | [원래 질문·답변](evidence/before/01-gateway-payments.png) | [양쪽 서비스 조회](evidence/after/review-q04-first.jpg), [결과](evidence/after/review-q04-second.jpg) |
| billing을 auth로 대체 | [등록 대상 식별](../all_total_vue_student/agent/targets.py) | [원래 질문·답변](evidence/before/06-billing.png) | [미등록 이름 확인](evidence/after/context-unknown-frame.jpg) |
| 서비스명 없는 요청에 auth 가정 | [대상 확인 후 계획 호출](../all_total_vue_student/agent/nodes.py) | [원래 질문·답변](evidence/before/05-login.png) | [서비스명 확인](evidence/after/review-q09-answer.jpg) |
| 정상 web에 DB 장애 매뉴얼 연결 | [상태 구분](../all_total_vue_student/agent/evidence.py), [검색 분기](../all_total_vue_student/agent/research.py) | [원래 질문·답변](evidence/before/03-web-auth.png) | [정상 web·지연 auth](evidence/after/context-healthy-answer.jpg) |
| 관측 근거와 다른 답변 | [수치·매뉴얼·절차 검증](../all_total_vue_student/agent/validation.py) | [원래 질문·답변](evidence/before/02-payments-cpu.png) | [검증 후 보고](evidence/after/review-q01-answer.jpg) |
| 사용자 이름을 비서의 이름으로 응답 | [사용자 발화의 이름 식별](../all_total_vue_student/agent/targets.py), [이름 응답](../all_total_vue_student/agent/nodes.py) | [원래 대화](evidence/before/07-name-recall.png) | [사용자 이름 응답](evidence/after/review-q10-answer.jpg) |

## 추가 기능

| 기능 | 구현 | 실행 증빙 |
|---|---|---|
| RAG 매뉴얼 검색 | [임베딩·캐시·유사도 검색](../all_total_vue_student/agent/retrieval.py), [MCP 검색 Tool](../all_total_vue_student/mcp_server.py) | [디스크 공간 부족 매뉴얼 연결](evidence/after/review-q03-answer.jpg) |
| 답변 근거 표시 | [근거 데이터 구성](../all_total_vue_student/agent/evidence.py), [웹 화면](../all_total_vue_student/web_chat.html) | [실제 관측·참고 매뉴얼](evidence/after/context-healthy-evidence.jpg) |
| 회귀 테스트·전후 비교 | [단위 테스트](../all_total_vue_student/tests/test_core.py), [비교 실행기](../evaluation/scripts/run_baseline.py) | [단위 테스트 기록](../evaluation/test-results/unit-tests-story.txt), [비교 보고서 화면](evidence/after/story-evaluation-report.jpg) |

## 측정 기준과 원시 기록

- [질문별 기대 대상·매뉴얼](../evaluation/data/cases.json)
- [개선 전 실행 기록](../evaluation/results/before/results.json)
- [개선 후 실행 기록](../evaluation/results/after/results.json)
- [지표별 비교와 한계](../evaluation/results/comparison/REPORT.md)
- [실제 앱·모델 응답 기록](../evaluation/results/contextual-captures/SUMMARY.md)
- [실제 MCP·SSE 통합 검증](../evaluation/results/integration/SUMMARY.md)
- [핵심 코드 발췌의 원문·파일 해시](evidence/after/code-complete/MANIFEST.json)

실행 화면은 기능의 동작을, 고정 데이터의 전후 기록은 선택 일치율을 보여준다. 조회 범위·문서 선택의 일치와 전체 원인 진단의 정확도는 구분한다.
