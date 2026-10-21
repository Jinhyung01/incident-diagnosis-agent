# 실행과 평가 재현

README에는 프로젝트 내용을, 이 문서에는 실행과 비교 조건을 둔다. 원본은 `day1/baseline/original_v2/`, 개선 버전은 `all_total_vue_student/`다. 교육용 모의 데이터이며 실제 서비스 장애나 조치 실행을 검증하지 않는다.

## 실행

Python 3.14 환경에서 검증했다. Python 3.11 이상과 Ollama가 필요하다.

```bash
cd all_total_vue_student
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
ollama pull qwen3:0.6b
ollama pull qwen3:8b
ollama pull bge-m3
cp .env.example .env
```

Ollama가 실행 중인 상태에서 백엔드를 연다.

```bash
LLM_BACKEND=ollama .venv/bin/python3 -m uvicorn server:app --host 127.0.0.1 --port 8100
```

다른 터미널에서 프런트엔드를 연다.

```bash
cd all_total_vue_student
BACKEND_URL=http://127.0.0.1:8100 .venv/bin/python3 -m uvicorn web_demo_server:app --host 127.0.0.1 --port 8600
```

브라우저에서 http://localhost:8600 에 접속한다. 기본 서버 시작은 기존 프로세스를 종료하거나 DB를 삭제하지 않는다. 개선 버전의 `sh/run_agent_ollma.sh`와 `sh/run_frontend.sh`도 같은 서버를 실행하며 사용 중인 포트에서는 종료한다. 원본의 강제 프로세스 종료·DB 초기화 동작은 제거했다. 보존 원본의 수업용 스크립트는 초기화 동작이 있으므로 구분한다.

매뉴얼 6개와 한·영 증상 메타데이터는 첫 검색 때 임베딩해 `.cache/runbooks.sqlite`에 저장한다. 문서·메타데이터·임베딩 모델명이 바뀌면 다시 만든다. `bge-m3:latest`의 검증 당시 digest는 평가 환경 기록에 남긴다. 모델 가중치가 같은 이름으로 바뀌면 캐시를 새 경로로 만들고 검색 결과를 재확인한다.

SQLite 대화 DB는 `session.db`이며 `SESSION_DB_PATH`로 변경할 수 있다. 브라우저는 같은 대화 ID를 유지한다. 새 대화 버튼은 새 ID를 만들며 기존 DB를 삭제하지 않는다.

## 단위 테스트와 원본 보존 확인

저장소 최상위 폴더에서 실행한다.

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 -m unittest discover -s all_total_vue_student/tests -v
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/check_preparation.py
```

두 번째 검사는 보존 원본·데이터·평가 지표를 확인한다. 개선된 작업 소스가 원본과 같은지는 요구하지 않는다. 최초 단계에서만 `--check-live-unchanged`를 사용할 수 있다.

## 고정 데이터 비교

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/run_baseline.py --backend ollama --output day2/results/new-before
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day1/scripts/run_baseline.py --source all_total_vue_student --improved --backend ollama --output day2/results/new-after
```

경로가 이미 있으면 덮어쓰지 않는다. 위 예시는 새 폴더명이다. 현재 비교 요약 스크립트는 제출에 사용한 기존 결과 폴더를 읽는다. 새 실행끼리 비교할 때에는 해당 입력 경로를 수정해 별도 결과로 관리한다.

원본과 개선 버전은 질문 20개, fixture, 모델 이름을 맞춘다. 실제 MCP 전송 대신 같은 고정 데이터 어댑터를 사용한 그래프 평가다. 개선 후 검색은 실제 bge-m3 임베딩을 사용한다. 인덱스 구축과 모델 워밍업은 요청 시간에서 제외한다. 초기 의도적 타임아웃도 양쪽에서 끈다.

생성 설정은 개선 전후가 다르다. 개선 후에는 think=false, 512토큰 상한, 호출 25초·요청 60초 상한, 최대 작성 2회를 적용한다. 답변 형식도 자유 서술에서 검증된 관측·원문 절차로 바뀌었다. 지연 차이를 RAG만의 효과로 해석하지 않는다. 원본 비용값은 가상 단가이므로 실제 비용 절감액으로 제시하지 않는다.

## 실제 MCP·HTTP·SSE·재시작 검증

```bash
PYTHONDONTWRITEBYTECODE=1 all_total_vue_student/.venv/bin/python3 day2/scripts/verify_integration.py --output day2/results/new-integration
```

8204/8704 포트가 비어 있어야 한다. 임시 서버와 별도 DB만 만들고 종료한다. 고정 모의 지표를 실제 MCP subprocess와 프록시로 조회하고 최초 의도적 실패의 재시도, 스트림 종료·내용 일치, 같은 thread/DB로 재시작한 뒤 이름의 사용자 역할을 확인한다. 장애 답변은 검증이 끝난 뒤 조각을 전송한다. 검증 전 초안의 토큰 스트리밍은 제공하지 않는다.

OpenAI 백엔드와 실제 운영 데이터, 부하·동시 사용자 성능은 개선 버전의 검증 범위에 포함하지 않았다.

## 발표 보완 시나리오 재현

이 시험은 기본 설정의 일반 실행과 별도다. 한 터미널에서 저장소 루트 기준으로 `.venv` Python을 사용해 `day2/scripts/serve_presentation_scenarios.py`를 실행하고, 다른 터미널에서 같은 파일에 `--proxy`를 붙여 실행한다. 브라우저에서 `http://127.0.0.1:8705/`를 연다. 기존 포트와 별개인 8205/8705를 사용한다.

- `billing-service 응답이 느려요`: 미등록·미조회 안내와 등록 서비스 이름 확인 요청.
- `web-01 상태를 확인해줘`: degraded·알림 없음 fixture로 정보 부족 안내와 매뉴얼 생략.
- `payments-service 응답이 느려요`: 보고 생성 의존성에 30초 지연, 요청 상한 8초로 시간 초과와 부분 관측 보존 확인.

일반 설정은 요청 60초·호출 25초다. 시험 래퍼가 이 환경에서만 제어 조건을 주입하고 실제 답변을 미리 만들거나 재생하지 않는다. 원시 이벤트는 `day2/results/presentation-scenarios/`에 기록한다. 이 요청을 일반 성능이나 기존 20건 통계에 합산하지 않는다. 사용 중인 포트를 먼저 확인하고 시험 종료 후 두 터미널에서 Ctrl+C로 종료한다.

## 질문·응답과 실제 모델 원문 기록

`day2/scripts/serve_capture_session.py`를 한 터미널에서 실행하고 다른 터미널에서 같은 파일에 `--proxy`를 붙여 실행한다. 브라우저는 `http://127.0.0.1:8706/`이며 8206/8706 포트를 먼저 확인한다. 모델과 의존성은 기본 실행과 같다. 별도 DB는 `day2/runtime/contextual-captures/`에 저장하며 공개하지 않는다.

순차로 질문하면 실제 보고 LLM의 반환값과 SSE 이벤트를 `day2/results/contextual-captures/`에 고유 파일명으로 저장한다. 답변을 대체하지 않는다. 동시 요청의 로그 격리는 이 시험의 범위가 아니다. 앱 화면의 최종 답변과 `raw_model_output`은 구분해 비교한다. `LLM_RAW.txt`는 저장된 JSON의 원문을 보여주는 파생 파일이다. 과거 기록은 덮어쓰지 않으며 이 실행은 기존 20건 통계에 합산하지 않는다. 종료할 때 두 터미널에서 Ctrl+C를 누른다.

## 같은 질문의 시간 초과·부분 근거 재현

발표 시연은 `day2/scripts/serve_presentation_scenarios.py --output day2/results/new-story-demo`와 별도 터미널의 같은 명령에 `--proxy`를 붙여 실행한다. 비어 있는 새 폴더를 지정해 이전 기록을 보존한다. 포트8205/8705가 비어 있어야 한다. 같은 payments·cache 질문을 UI에 입력하면 생성 의존성30초 지연·요청 상한8초 시험이 실행된다. 일반 기본60초와 구분한다. 원시 이벤트·실제 화면은 기존20건 시간 통계에 합산하지 않는다.
