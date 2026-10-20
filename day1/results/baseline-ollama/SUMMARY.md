# 개선 전 평가 실행 요약

- 백엔드: `ollama`
- 모델: `qwen3:0.6b` / `qwen3:8b`
- 완료 기록: 20/20; 실행 오류: 4
- 최종 응답 완료: 16/20 (80.0%)
- 평가 범위: 원본 v2 그래프 + 고정 데이터 MCP 어댑터. 실제 MCP 전송 및 웹 UI는 이 실험의 검증 대상이 아님.
- 토큰 수는 Ollama 응답에서 수집. cost_usd는 가상 비교값이며 실제 청구액이 아님.
- 타임아웃 난 LLM 호출은 토큰 사용량을 반환하지 않으므로 기록된 토큰 합계는 전체 생성량이 아님.
- 설정된 반복 횟수: 사례별 1회. 작은 평가 세트의 결과이며 운영 전체의 성능을 대표하지 않음.
- 의미·사실 정확성은 자동 채점하지 않았음. review 체크리스트에 따른 사람 검토 필요.

| 자동 지표 | 결과 |
|---|---|
| 요청한 등록 대상 수집률 | 17/20 (85.0%) |
| 조회 단계의 대상 범위 일치 | 15/20 (75.0%) |
| 대상 범위 일치 + 최종 응답 완료 | 12/20 (60.0%) |
| 검색 단계의 단일 정답 매뉴얼 Top-1 | 11/12 (91.7%) |
| 단일 정답 매뉴얼 적중 + 최종 응답 완료 | 8/12 (66.7%) |
| 매뉴얼 불필요 사례의 불필요 검색 방지 | 2/6 (33.3%) |
| 성공한 사례의 처리 시간 중앙값 | 35.94초 |

대상 수집률은 대상 개수로, 대상 범위 일치는 사례 수로 계산한다. 대상 범위는 수집에 성공한 서비스 집합 기준이며 실패한 호출 시도는 별도 확인한다.
단일 정답 Top-1은 정답 문서가 하나인 사례만 포함한다. 검색·수집 뒤 응답이 실패할 수 있어 단계별 지표와 완료 지표를 나눴다.
매뉴얼 불필요 사례에는 일반 대화도 포함된다. 이 값은 정상 서비스 처리만의 성공률이 아니다.

| 데이터 구분 | 기록 | 최종 응답 완료 | 시간 초과 등 오류 |
|---|---:|---:|---:|
| development | 12 | 9 | 3 |
| evaluation | 6 | 5 | 1 |
| supplemental | 2 | 2 | 0 |

| ID | 실제 조회 대상 | 매뉴얼 | 시간(초) | 오류 |
|---|---|---|---:|---|
| D01 | payments-service | cpu-spike | 305.52 | 있음 |
| D02 | cache-service | memory-leak | 37.45 | 없음 |
| D03 | log-service | disk-full | 144.43 | 없음 |
| D04 | auth-service | high-latency | 99.05 | 없음 |
| D05 | gateway-service | network-timeout | 38.52 | 없음 |
| D06 | payments-service | cpu-spike | 306.55 | 있음 |
| D07 | web-01 | db-down | 41.44 | 없음 |
| D08 | auth-service | high-latency | 34.30 | 없음 |
| D09 | auth-service | high-latency | 27.15 | 없음 |
| D10 | web-01 | db-down | 18.49 | 없음 |
| D11 | payments-service | cpu-spike | 304.06 | 있음 |
| D12 | payments-service | cpu-spike | 41.69 | 없음 |
| E01 | payments-service | cpu-spike | 303.51 | 있음 |
| E02 | cache-service | memory-leak | 34.42 | 없음 |
| E03 | gateway-service | network-timeout | 45.66 | 없음 |
| E04 | auth-service | db-down | 29.10 | 없음 |
| E05 | payments-service, web-01 | db-down | 30.16 | 없음 |
| E06 | payments-service | cpu-spike | 38.35 | 없음 |
| M01 | 없음 | 없음 | 1.43 | 없음 |
| M02 | 없음 | 없음 | 2.37 | 없음 |
