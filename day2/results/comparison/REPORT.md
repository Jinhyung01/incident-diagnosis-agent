# 고정 데이터 개선 전후 비교

동일한 원본 v2 기준 질문 20개·고정 모니터링 데이터·qwen3:0.6b/8b를 사용했다. 각 질문의 세션을 분리했고 일반 대화 보조 사례 2개를 포함한다. 실제 MCP 전송 대신 데이터 어댑터를 사용한 그래프 평가다.

| 지표 | 개선 전 | 개선 후 |
|---|---:|---:|
| 최종 응답 완료 | 16/20 | 20/20 |
| 요청한 등록 대상 수집 | 17/20 | 20/20 |
| 조회 대상 범위 일치 | 15/20 | 20/20 |
| 단일 정답 매뉴얼 Top-1 | 11/12 | 12/12 |
| 불필요한 매뉴얼 검색 생략 | 2/6 | 6/6 |
| 성공 응답 시간 중앙값 | 35.94초 (16건) | 4.45초 (20건) |

개선 후 응답 구성: 구조화 검증 통과 13건, 관측·대상 확인 안내 4건, 일반 대화 2건, 생성·검증 실패 후 안내 1건.

E06(등록·미등록 혼합 요청)은 두 번의 생성에서도 서비스 범위를 벗어난 필드가 남아 검증에 실패했다. 강제로 통과시키지 않고 실제 payments 관측과 매뉴얼 원문, billing 미등록 안내를 반환했다. 응답 완료가 모든 LLM 초안의 성공을 뜻하지 않는다.

양쪽 모두 완료한 16건만 비교하면 중앙값은 35.94초 → 4.45초다.

## 비교 조건과 해석

- 모델 이름·평가 데이터 해시는 일치한다. 개선 전 원본은 think/생성량 제한 설정이 없고 호출 읽기 제한이 300초다.
- 개선 후 think=false, 생성 512토큰 상한, 호출 25초·전체 요청 60초 상한, 최대 작성 2회를 적용했다. 사고·답변 형식과 작업 단계도 바뀌었다.
- 생성량·분기·출력 형식 변경이 지연 차이에 함께 영향을 줬다. RAG 또는 모델 성능만의 효과로 해석하지 않는다.
- 검색은 기존 6개 매뉴얼 본문에 한·영 증상 설명을 보강해 임베딩했다. 데이터 보강과 RAG가 함께 바뀌었다.
- 6개 문서·20개 질문에서 얻은 값이며 운영 환경의 정확도나 통계적 유의성을 뜻하지 않는다.
- 같은 입력 중 원래 auth 기본 처리를 기대했던 항목은 이번 정책의 대상 확인 동작을 기준으로 평가한다.
- 시간 초과 호출의 토큰 사용량은 누락될 수 있다. 원본 가상 비용을 실제 절감액으로 제시하지 않는다.

## 사례별 결과

| ID | 개선 전 조회 | 개선 후 조회 | 전/후 매뉴얼 | 전/후 시간(초) | 후 응답 유형 |
|---|---|---|---|---:|---|
| D01 | payments-service | payments-service | cpu-spike / cpu-spike | 305.52 실패 / 4.39 | validated |
| D02 | cache-service | cache-service | memory-leak / memory-leak | 37.45 / 4.47 | validated |
| D03 | log-service | log-service | disk-full / disk-full | 144.43 / 4.08 | validated |
| D04 | auth-service | auth-service | high-latency / high-latency | 99.05 / 4.51 | validated |
| D05 | gateway-service | gateway-service, payments-service | network-timeout / network-timeout,cpu-spike | 38.52 / 8.05 | validated |
| D06 | payments-service | cache-service, payments-service | cpu-spike / cpu-spike,memory-leak | 306.55 실패 / 8.01 | validated |
| D07 | web-01 | auth-service, web-01 | db-down / high-latency | 41.44 / 7.60 | validated |
| D08 | auth-service | 없음 | high-latency / 없음 | 34.30 / 0.01 | observation |
| D09 | auth-service | 없음 | high-latency / 없음 | 27.15 / 0.00 | observation |
| D10 | web-01 | web-01 | db-down / 없음 | 18.49 / 0.56 | observation |
| D11 | payments-service | payments-service | cpu-spike / cpu-spike | 304.06 실패 / 5.16 | validated |
| D12 | payments-service | payments-service | cpu-spike / cpu-spike | 41.69 / 4.74 | validated |
| E01 | payments-service | payments-service | cpu-spike / cpu-spike | 303.51 실패 / 4.40 | validated |
| E02 | cache-service | cache-service | memory-leak / memory-leak | 34.42 / 4.71 | validated |
| E03 | gateway-service | gateway-service | network-timeout / network-timeout | 45.66 / 5.07 | validated |
| E04 | auth-service | auth-service | db-down / db-down | 29.10 / 4.43 | validated |
| E05 | payments-service, web-01 | payments-service, web-01 | db-down / 없음 | 30.16 / 0.70 | observation |
| E06 | payments-service | payments-service | cpu-spike / cpu-spike | 38.35 / 13.38 | fallback |
| M01 | 없음 | 없음 | 없음 / 없음 | 1.43 / 0.00 | chat |
| M02 | 없음 | 없음 | 없음 / 없음 | 2.37 / 0.00 | chat |
