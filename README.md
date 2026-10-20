# 운영 장애 진단 AI 에이전트 개선

`gateway-service`에서 `payments-service`로 가는 요청의 타임아웃을 조사했을 때, 원본 에이전트는 gateway만 조회하고 답변했습니다. 이 프로젝트는 수업에서 제공한 운영 장애 진단 에이전트의 **조사 대상 누락과 근거 없는 단정**을 줄이는 과제입니다.

## 확인한 문제

| 입력·상황 | 개선 전 동작 | 바꿀 동작 |
|---|---|---|
| gateway → payments 타임아웃 조사 | gateway만 조회 | 요청 범위의 두 서비스를 조회하고 각각의 결과 표시 |
| 등록되지 않은 billing-service 조회 | auth-service를 조회해 답변 | 미등록 대상임을 알리고 확인 요청 |
| 정상 web-01 조회 | DB Down 매뉴얼 검색 | 정상 상태를 알리고 불필요한 장애 매뉴얼 검색 생략 |
| cache 메모리 89% | 매뉴얼의 90% 이상 조건과 달리 즉시 재시작 권고 | 현재 값과 조치 조건을 구분해 안내 |

각각 D05, D08, D10, D02 사례에서 확인했습니다. [개선 전 실행 기록](day1/results/baseline-ollama/SUMMARY.md)과 [근거 대조 메모](day1/results/baseline-ollama/REVIEW.md)에서 입력·조회 결과·답변을 확인할 수 있습니다.

## 진행 상태

2026-10-20, Day 1 기준입니다.

| 구분 | 상태 |
|---|---|
| 제공된 원본 분석·보존 | 완료 |
| 평가 질문 20개·고정 데이터·평가 실행기 | 작성 및 개선 전 실행 완료 |
| 대상 누락·임의 대체 방지 | 구현 예정 |
| RAG 매뉴얼 검색·답변 근거 표시 | 구현 예정 |
| 수치·대상·조치 조건 검증, 시간 초과 처리 | 구현 예정 |
| 개선 후 평가·화면 캡처·발표자료 | 미완료 |

## 개선 전 측정 결과

원본 v2 그래프를 `qwen3:0.6b` / `qwen3:8b`로 사례별 1회 실행했습니다. 무작위 모니터링 값은 고정 데이터로 교체했습니다.

| 항목 | 결과 |
|---|---:|
| 최종 응답 완료 | 16/20건 |
| 시간 초과 | 4/20건, 약 303~307초 |
| 요청한 등록 대상 수집 | 17/20개 대상 |
| 단일 정답 매뉴얼 검색 적중 | 11/12건 |

응답 완료는 답변이 정확하다는 뜻이 아닙니다. 예를 들어 메모리 매뉴얼을 찾았어도 재시작 조건을 잘못 적용한 사례가 있었습니다. 매뉴얼 검색 정확도와 최종 답변의 근거 일치를 따로 평가합니다.

이 측정은 고정 데이터 어댑터를 사용한 그래프 실험입니다. 실제 MCP 전송과 웹 UI를 포함한 통합 검증, 반복 실행, 개선 후 비교는 남아 있습니다. [실험 조건과 전체 결과](day1/results/baseline-ollama/SUMMARY.md)를 참고하세요.

## 실행

현재 확인한 환경은 macOS, Python 3.14.7, Ollama입니다. 패키지 버전은 [실행 환경 기록](day1/environment.json)과 [버전 목록](day1/requirements-baseline.txt)에 있습니다. 새 환경에서의 설치 재현은 아직 확인하지 않았습니다.

저장소 최상위 폴더에서 가상환경을 준비합니다.

```bash
cd all_total_vue_student
bash sh/setup_venv.sh
```

Ollama를 실행한 상태에서 모델을 준비합니다. 이미 설치되어 있다면 그대로 사용합니다.

```bash
ollama pull qwen3:0.6b
ollama pull qwen3:8b
```

같은 폴더에서 백엔드를 실행합니다. 아래 명령은 LangSmith 전송을 끄고 로컬 모델을 사용합니다.

```bash
LANGCHAIN_TRACING_V2=false LANGSMITH_TRACING=false \
LLM_BACKEND=ollama SUPERVISOR_VERSION=v2 .venv/bin/python3 server.py
```

새 터미널을 열고 저장소 최상위 폴더에서 프론트엔드를 실행합니다.

```bash
cd all_total_vue_student
.venv/bin/python3 web_demo_server.py
```

브라우저에서 `http://localhost:8600`에 접속합니다. 종료는 각 터미널에서 `Ctrl+C`로 합니다. 기존 `sh/run_agent_ollma.sh`는 재기동 시 대화 DB를 삭제하므로, 위에서는 서버를 직접 실행합니다.

LangSmith를 사용하려면 `.env.example`을 참고해 별도 `.env`에 설정합니다. OpenAI 실행 방법 등 기존 기능은 [베이스 프로젝트 안내](all_total_vue_student/doc/README.md)에 있습니다.

평가 실행 방법과 결과 해석은 [Day 1 평가 안내](day1/README.md)를 참고하세요.

## 코드와 자료

- `all_total_vue_student/`: 수업에서 제공한 애플리케이션. 현재 동작 코드는 원본과 동일합니다.
- `day1/baseline/`: 개선 전 비교용 사본(`original_v2/`)과 해시 목록(`manifest.json`).
- `day1/evaluation/`, `day1/scripts/`: 이번 과제에서 작성한 평가 데이터와 실행 도구.

베이스는 FastAPI·Vue 3·LangGraph와 MCP Tool/Resource/Prompt를 사용합니다. 이번 과제에서는 대상 검증·근거 검증 모듈과 RAG 검색을 추가할 계획입니다. 기존 기술과 새로 구현한 부분을 구분해 보고합니다.

실습 데이터에는 실제 로그·시계열·서비스 의존 관계가 없습니다. 이 자료만으로 공통 원인이나 복구 완료를 확정할 수 없습니다. 수업 PDF, 실행용 키, 개인 대화 DB는 저장소에서 제외합니다.
