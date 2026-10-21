> 이 문서는 10/20 개선 전 준비 기록입니다. 이후 구현과 최종 결과는 [결과 보고서](../REPORT.md)를 확인해주세요.

# 개선 전 평가

원본 v2의 고정 데이터 평가에 사용한 자료와 재현 방법이다.

## 평가 자료

| 항목 | 파일·위치 |
|---|---|
| 원본 v2 47개 파일 보존 | `baseline/original_v2/` |
| 원본과 사본의 SHA-256 목록 | `baseline/manifest.json` |
| 실행 환경 및 패키지 버전 | `environment.json`, `requirements-baseline.txt` |
| 평가 질문 20개 | `evaluation/cases.json` |
| 공통 고정 데이터 및 시나리오 | `evaluation/fixtures.json` |
| 원본 그래프 평가 실행기 | `scripts/run_baseline.py` |
| 보존·데이터·지표 검사 | `scripts/check_preparation.py` |
| 실행 결과 요약 | `scripts/summarize_results.py` |
| 로컬 실모델 개선 전 실측 20건 | `results/baseline-ollama/` — 16건 응답 완료, 4건 시간 초과 |
| 개선 전 답변 근거 대조 메모 | `results/baseline-ollama/REVIEW.md` — AI 보조 검토, 사람의 최종 확인 필요 |

원본 애플리케이션의 동작 코드는 아직 수정하지 않았다. 배포용 `.env.example`의 키 값만 자리표시자로 치환했다. 실행용 `.env`는 유지한다.

원본 평가에서 4건의 ReadTimeout이 발생했다. 성공·실패 기록을 모두 저장했다. 후속 구현에는 생성량·처리 시간 상한과 실패 응답을 포함한다.

준비 검사는 원본 사본 47개 해시, 동작 코드 보존, 평가 데이터 20개의 형식·기대값, 데이터 격리, 지표 경계 조건, 재시도 제어를 확인했다. 개선 기능의 테스트와 개선 후 성능 검증은 Day 2 작업이다.

## 평가 데이터 구성

- 개발용 12건: 대상 누락·미등록·모호한 요청·정상 상태·로그 근거 부족·조치 조건
- 평가용 6건: 바꿔 쓴 표현·DB 장애 시나리오·정상 복수 대상·등록/미등록 혼합
- 보조 2건: 인사·이름 기억

`expected_*`는 이번 과제의 기대 동작이다. 실제 측정값은 `results/`에 저장한다. 평가용 질문은 검색 기준을 조정하는 데 사용하지 않는다.

## 결과 읽기

- 최종 응답 완료는 호출이 끝났다는 뜻이다. 답변의 사실 정확성을 뜻하지 않는다.
- 대상 수집률의 분모는 조회해야 할 등록 대상 수다. 전체 질문 수도 20이지만 서로 다른 값이다.
- 대상 범위 일치는 수집에 성공한 서비스 집합을 비교한다. 실패한 조회 시도나 추가 확인 질문의 적절성은 별도 확인한다.
- 매뉴얼 Top-1은 단일 정답을 지정한 12개 사례에만 계산한다. 검색 후 최종 답변이 시간 초과로 끝날 수도 있다.
- 성공 응답의 시간 중앙값은 시간 초과 사례를 제외한 값이다. 실패 시간과 완료율도 함께 제시한다.
- D09(로그인 지연)의 대상 확인 기대값은 등록 별칭이 없다는 정책에 따른다. 별칭 정책을 바꾸면 평가 기대값 변경도 기록한다.
- [근거 대조 메모](results/baseline-ollama/REVIEW.md)는 AI 보조 검토다. 사람의 최종 판정은 미완료다.

## 명령

프로젝트 최상위 폴더에서 실행한다.

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/check_preparation.py
```

Fake로 실행기 동작만 확인:

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/run_baseline.py \
  --backend fake --output day1/results/new-smoke
```

로컬 Ollama에서 대표 사례 실행:

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/run_baseline.py \
  --backend ollama --cases D06,D08,M02 --output day1/results/new-baseline
```

결과 요약:

```bash
all_total_vue_student/.venv/bin/python3 day1/scripts/summarize_results.py day1/results/new-baseline
```

결과 경로가 이미 존재하면 덮어쓰지 않는다. 새 폴더 이름을 사용한다.

## 비교 조건

- 원본 v2를 비교 기준으로 사용한다.
- 랜덤 모니터링 수치를 고정하고, 실습용 최초 타임아웃은 기본 평가에서 끈다.
- 그래프 내 태스크당 0.35초 지연은 원본 그대로다.
- 각 질문의 세션은 분리하고, 이름 기억만 2턴을 이어서 실행한다.
- 평가기는 기존 웹 서버·세션 DB를 사용하지 않는다.
- 실제 MCP 전송을 거치지 않는 테스트 어댑터이므로, 최종 검증에는 실제 MCP와 웹 UI 통합 테스트를 추가해야 한다.
- 원인 확정·허위 로그 분석 등 의미 오류는 원문 근거와 수동으로 대조한다. 자동 키워드 경고를 정확도 점수로 취급하지 않는다.
