"""Build the submission report from saved results and explicit limitations."""
import json
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=json.loads((ROOT/'evaluation/results/comparison/summary.json').read_text())
rag=json.loads((ROOT/'evaluation/results/comparison/retrieval-overhead.json').read_text())
repeats=json.loads((ROOT/'evaluation/results/comparison/repeats.json').read_text())
a,b=s['after'],s['before']
search_median=statistics.median(x['seconds'] for x in rag['searches'])
md=f'''# 서비스 장애 진단 AI 에이전트 개선

이진형 · 과제 1: Base AI Project 개선 · 2026-10-21 구현·검증

[발표자료 다운로드](output/presentation/incident-diagnosis-agent-submission.pptx) · [발표자료 보기](https://canva.link/0qx76m2u9f9d6vm)

## 1. 주제와 문제

실습 1인 Base AI Project 개선을 선택했다. 제공된 베이스는 서비스 장애 진단 AI 에이전트다. 웹 채팅으로 서비스 이름과 증상을 입력하면 LLM이 조사 계획을 세우고 MCP로 모니터링 지표·매뉴얼을 조회해 보고서를 작성한다. FastAPI·LangGraph·SQLite 대화 이력이 있는 기존 구조를 활용했다. 대표 문제는 `payments-service랑 cache-service 둘 다 저하됐는데 공통 원인이 있는지 분석해줘`라는 요청에서 payments만 조사하고 cache를 포함한 원인을 추정하는 동작이었다.

목표는 요청한 대상을 빠짐없이 조사하고, 관측한 사실과 추가 확인이 필요한 내용을 구분하는 것이다. 실제 서버 조치를 자동 실행하거나 근본 원인을 확정하는 기능은 범위에 넣지 않았다.

## 2. 개선 사항과 추가 기능

| 개선 | 변경한 동작 | 확인 사례 |
|---|---|---|
| 조사 대상 누락 방지 | 등록 대상 전체 추출·대상별 조회 작업 재구성 | D05·D06·D07 다중 대상 |
| 미등록 대상 처리 | 다른 서비스로 대체하지 않고 등록 이름 확인 요청 | D08 미등록, E06 혼합 |
| 상태별 매뉴얼 선택 | 정상·정보 부족은 검색 생략, 서비스별 관측 알림으로 검색 | D10 정상, E05 정상 복수 대상 |
| 근거와 조치 조건 검증 | 서비스·수치·문서·절차 번호 대조, 원인 확정 거절, 조건은 원문 출력 | D11 로그 미수집, D12 CPU 89.1%와 알림 91% |

추가한 기능은 RAG 매뉴얼 검색, 실제 조회 서비스·매뉴얼·미확인 사항을 보여주는 근거 화면, 같은 질문·고정 데이터의 회귀 평가다.

미등록·미명시 요청의 auth 기본 처리는 원래 설계였다. 이 부분은 원래 회귀 기준의 오류가 아니라 대상 확인 안내로 바꾼 정책 개선이다. 이름 기억은 새 주요 기능으로 늘리지 않고 사용자 역할과 서버 재시작 유지의 회귀 검증에 포함했다.

## 3. 사용 기술과 변경 범위

| 기술 | 베이스에서 활용 | 직접 추가·변경 |
|---|---|---|
| LangGraph·FastAPI | 그래프 흐름·HTTP·SSE·수명 관리 | 범위 확인·수집·검색·검증 노드 연결 |
| MCP | 모니터링 Tool·매뉴얼 Resource·절차 Prompt | search_runbooks Tool, 검색 결과와 원문 연결 |
| RAG | 없음 | bge-m3, 한·영 증상 설명과 매뉴얼 본문 임베딩, SQLite 저장, 코사인 검색 |
| 의존성 주입·모듈화 | SupervisorDeps | 대상 식별·수집·검색·보고·검증을 분리, 검색 의존성 교체 |
| 테스트·평가 | 수업의 회귀 입력 | 핵심 단위 테스트 31개, 고정 데이터 20개, 대표 사례 3회 반복, 실제 MCP·SSE·재시작 검증 |
| 화면 | 수업 Vue 화면은 원본에 보존 | 외부 CDN 없는 HTML·JavaScript, 근거와 미확인 사항 표시 |

LLM은 계획을 제안하고 수집한 관측과 문서의 절차 번호를 구조화해 정리한다. 실제 조회 범위는 코드가 제한한다. 검증된 선택을 매뉴얼 원문으로 출력해 조건을 재작성하지 않는다. 이는 자유 생성 문장 전체의 의미를 검증하는 범용 사실성 평가기는 아니다.

MCP 서버에는 `search_runbooks` Tool을 추가했다. `retrieval.py`가 임베딩 검색을 수행하고 `research.py`가 선택한 매뉴얼 원문을 연결한다. 기존 `SupervisorDeps`에 `searcher`를 추가해 실제 MCP 검색과 고정 평가 어댑터를 교체한다. `graph.py`·`nodes.py`는 범위 확인·수집·검색·검증 흐름을 연결하고, 단위 테스트는 대상 누락·잘못된 수치·부분 실패·시간 제한 같은 분기를 확인한다.

기존 기술을 직접 새로 만들었다고 주장하지 않는다. 전문 멀티에이전트 확장이나 LangSmith 연결 검증은 이번 성과에 포함하지 않았다. OpenAI 경로는 보존 원본에 있으며 개선 버전은 Ollama를 검증했다.

## 4. 실행 결과로 확인한 문제와 개선

개선 전후 같은 질문을 입력했다. 모의 지표는 실행 시점에 따라 달라지므로 CPU·메모리 값의 차이를 개선 성과로 비교하지 않는다. 정량 평가는 다음 절의 고정 질문·지표 결과다.

### 개선 1. 다중 서비스 조사 누락

최초 payments·cache 요청에서는 payments만 수집하고 공통 원인 후보를 제시했다. cache 지표와 공유 의존 관계가 없어 공통 원인을 판단할 근거가 부족했다.

![개선 전 payments·cache 질문과 답변](docs/evidence/before/04-payments-cache.png)

요청에서 등록 서비스 전체를 직접 추출하고 그 대상별로 조회 작업을 다시 구성했다. 같은 질문에서 두 서비스를 각각 조회하고, CPU·메모리 매뉴얼을 따로 연결했다. 의존 관계·동시 변화 자료가 없어 공통 원인은 미확인으로 남긴다.

![같은 질문의 개선 응답 1](docs/evidence/after/review-q06-first.jpg)

![같은 실행의 개선 응답 2](docs/evidence/after/review-q06-second.jpg)

### 개선 2. 미등록 대상의 임의 대체

최초 billing 요청에서 실제 수집한 대상은 auth였다. 이는 원래 기본 정책이지만 요청 대상과 조회 대상이 달라지는 문제로 보아 정책을 변경했다.

![개선 전 billing 질문과 auth 조회](docs/evidence/before/06-billing.png)

등록 목록과 대조하고, 미등록이면 다른 서비스의 조회·보고 생성을 생략한 뒤 확인할 이름을 요청한다. 이 응답은 LLM 보고 생성이 아닌 코드 안내다.

![같은 billing 질문의 확인 요청](docs/evidence/after/context-unknown-frame.jpg)

### 개선 3. 정상·장애·정보 부족과 매뉴얼 선택

최초 web·auth 요청은 web이 healthy·알림0건인데 db-down 문서를 선택했다.

![개선 전 web·auth 질문과 DB 문서](docs/evidence/before/03-web-auth.png)

상태를 먼저 구분하고 정상은 검색을 생략한다. 같은 질문에서 web은 정상으로, auth는 관측 알림에 맞는 지연 문서로 보고한다. 최초41%·51.5%와 아래34%·48%는 다른 시점의 모의 값이다.

![같은 web·auth 질문의 개선](docs/evidence/after/context-healthy-answer.jpg)

### 개선 4. 수집 근거와 답변·조치 조건의 대조

최초 payments 답변에는 로그 분석 결과라는 표현이 있지만 실제 로그는 수집하지 않았다.

![개선 전 payments CPU 질문과 로그 분석 표현](docs/evidence/before/02-payments-cpu.png)

구조화된 서비스·수치·문서·절차 번호를 검증하고, 검증 후 절차는 원문으로 출력한다. 실제 로그 미수집·조치 미실행을 표시한다. 자유 생성 문장 전체의 의미 검증이나 조건 충족의 자동 판정은 아니다.

![같은 payments 질문의 개선](docs/evidence/after/review-q01-answer.jpg)

### 추가 기능 1. RAG 대응 매뉴얼 검색

서비스별 관측 알림을 bge-m3로 임베딩하고 SQLite에 저장한6개 문서와 코사인 유사도를 계산한다. 임계값0.35이상 후보에서 첫 문서를 선택해 MCP Resource로 원문을 읽는다. 실제 log 질의에서는 disk-full과 유사도0.673이 표시된다. 유사도는 정답 확률이 아니다.

![RAG 검색의 실제 결과](docs/evidence/after/review-q03-answer.jpg)

### 추가 기능 2. 실제 조회 근거와 미확인 사항 화면

서버의 실제 수집 객체를 최종 이벤트에 포함하고 UI가 서비스·관측 수치·문서 표를 구성한다. 모델 문장과 별도로 근거를 확인할 수 있다. web의 문서 없음과 auth의 지연 문서·유사도, 실제 로그 미수집 등을 보여준다.

![실제 수집 객체로 표시한 근거](docs/evidence/after/context-healthy-evidence.jpg)

### 추가 기능 3. 회귀 테스트·동일 입력 비교 실행기

질문·고정 지표·분리 세션으로 실행하고 결과 JSON에서 대상 수집·문서 선택·응답 상태·시간을 집계해 보고서를 만든다. 아래는 보존된20건 원시 결과에서 다시 집계한 실제 보고서 화면이며 LLM20건을 새로 실행한 결과는 아니다. 단위 테스트31개도 별도로 다시 통과했다.

![평가 실행기가 실제 생성한 비교 보고서](docs/evidence/after/story-evaluation-report.jpg)

[질문별 개선 결과와 증빙](docs/EVIDENCE.md) · [추가 UI·원시 기록](evaluation/results/contextual-captures/SUMMARY.md) · [단위 테스트31개](evaluation/test-results/unit-tests-story.txt)

## 5. 동일 입력의 개선 전후 비교

20건 비교 후 미등록 확인 요청과 시간 초과 안내 문구를 보완했다. 아래 수치는 문구 보완 전 측정 기록이며 전체 통계를 다시 측정하지 않았다. 조사·검색·검증·제한 로직은 유지하고, 새 문구·실패 분기는 별도 실제 UI 시험과 단위 테스트로 확인했다.

질문 20개·고정 모니터링 데이터·qwen3:0.6b/8b 설정·세션 분리를 맞췄다. 데이터 해시 일치를 확인했다. 실제 MCP 전송 대신 같은 고정 데이터 어댑터를 사용한 그래프 평가이며, 임베딩 검색은 실제 bge-m3를 사용했다.

| 지표 | 개선 전 | 개선 후 |
|---|---:|---:|
| 최종 응답 완료 | {b['completed']}/20 | {a['completed']}/20 |
| 요청한 등록 대상 수집 | {b['targets_matched']}/{b['targets_expected']} | {a['targets_matched']}/{a['targets_expected']} |
| 조회 대상 범위 일치 | {b['target_scope']}/20 | {a['target_scope']}/20 |
| 단일 정답 매뉴얼 Top-1 | {b['top1']}/{b['single_cases']} | {a['top1']}/{a['single_cases']} |
| 불필요한 매뉴얼 검색 생략 | {b['none_pass']}/{b['none_cases']} | {a['none_pass']}/{a['none_cases']} |
| 성공 응답 시간 중앙값 | {b['median_success_seconds']:.2f}초·16건 | {a['median_success_seconds']:.2f}초·20건 |

![전후 측정 기록](docs/evidence/after/comparison.jpg)

응답 완료에는 안내 응답도 포함한다. 개선 후 20건은 구조화 검증 통과 13건, 관측·대상 확인 안내 4건, 일반 대화 2건, 검증 실패 후 안내 1건이다. E06은 두 번의 생성에서도 서비스 범위를 벗어나 반려됐고 payments 관측·매뉴얼 원문과 billing 미등록 안내를 반환했다.

대상 수집률은 요청마다 필요한 서비스 대상을 합산한 건수를, 범위 일치는 질문 수를 분모로 한다. Top-1은 정답 문서가 하나인 12건만 계산하고, 검색 불필요 6건에는 일반 대화 2건도 포함한다. 양쪽 모두 완료한 16건만 비교한 중앙값은 {s['paired_median_before_seconds']:.2f}초 → {s['paired_median_after_seconds']:.2f}초다.

개선 후에는 think=false, 512토큰 상한, 호출·요청 제한, 구조화 출력과 분기 변경을 적용했다. 이 변경들이 지연 차이에 함께 영향을 줬으므로 RAG만의 효과로 해석하지 않는다. 문서 본문에 한·영 증상 설명도 보강했다. 원본의 가상 비용이나 시간 초과로 누락된 토큰을 실제 비용 절감으로 제시하지 않는다.

![전후 실행 기록으로 만든 비교 그래프](docs/images/selection-comparison.png)

[그래프 집계 데이터](evaluation/results/comparison/presentation-metrics.json) · [그래프 데이터 생성 코드](evaluation/scripts/build_presentation_metrics.py)

### 선택 정확성을 먼저 확인

필요한 서비스 조회는17/20건(85%)에서20/20건, 조회 대상 집합 일치는15/20문항(75%)에서20/20문항, 단일 정답 매뉴얼 선택은11/12문항(91.7%)에서12/12문항으로 바뀌었다. 세 지표는 대상·문서 선택의 일치율이며 전체 원인 진단의 정답률은 아니다. 시간은 보조 지표로 구분한다.

### 판정 기준과 실제 개선 사례

| 항목 | 판정 방식 | 확인된 변화 |
|---|---|---|
| 필요한 서비스 수집 | 질문별 기대 등록 대상과 실제 모니터링 호출 목록 교집합을 합산 | 17/20 → 20/20. D05의 payments, D06의 cache, D07의 auth 누락 보완 |
| 조회 범위 일치 | 실제 대상 집합과 기대 대상 집합이 정확히 같은 질문 수 | 15/20 → 20/20. 누락 3건과 D08·D09의 auth 대체 조회 2건 개선 |
| 단일 정답 매뉴얼 | 정답 문서가 하나인 12개 질문에서 첫 조회 문서를 대조 | 11/12 → 12/12. D07의 db-down 선택을 high-latency로 변경 |
| 처리 시간 | 전후 모두 완료한 같은 16개 질문의 그래프 실행 시간 중앙값 | 35.94초 → 4.45초. 화면·통신·워밍업·인덱스 구축 제외 |
| 최종 응답 반환 | 실행 예외 없이 결과를 반환한 질문 수 | 16/20 → 20/20. 확인·실패 안내를 포함하며 답변 정답률이 아님 |

기대 대상·문서는 `evaluation/data/cases.json`, 실제 호출·선택·시간은 개선 전후 `results.json`에 기록돼 있다. 이 기준은 등록되지 않거나 명시되지 않은 대상을 확인하도록 변경한 정책을 포함한다. 실제 채팅 캡처는 기능 동작을 보여주고, 아래 평가 보고서 캡처는 같은 조건의 정량 집계를 보여준다.

![실제 실행 기록의 사례별 전후 비교](docs/evidence/after/evaluation-cases.jpg)

![측정 기준과 집계 결과](docs/evidence/after/evaluation-criteria.jpg)

[개선 전 원시 실행 기록](evaluation/results/before/results.json) · [개선 후 원시 실행 기록](evaluation/results/after/results.json) · [평가 정의](evaluation/data/cases.json) · [집계 코드](evaluation/scripts/build_evaluation_evidence.py)

### 반복 실행과 검색 부담

대표 개발 사례를 양쪽에서 각 3회 실행했다. 단일 입력의 최저 시간을 성능으로 고르지 않고 중앙값을 사용했다.

| 사례 | 원본 중앙값 | 개선 중앙값 | 조회 범위 일치 전/후 |
|---|---:|---:|---:|
'''
for id,label in [('D02','메모리'),('D05','gateway·payments'),('D08','미등록 billing')]:
    x,y=repeats['before'][id],repeats['after'][id]
    md+=f"| {id} {label} | {x['median_seconds']:.2f}초 | {y['median_seconds']:.3f}초 | {x['target_scope_passes']}/3 → {y['target_scope_passes']}/3 |\n"
md+=f'''
별도 6개 문서 인덱스 구축은 {rag['build_seconds']:.3f}초, 개발용 증상 5개×3회 검색의 중앙값은 {search_median:.3f}초였다. 이미 설치된 모델과 OS 캐시를 사용했고 다운로드·서버 시작 시간은 제외했다. 전체 요청 측정에서는 인덱스 구축과 모델 워밍업을 제외했다.

[사례별 결과와 조건](evaluation/results/comparison/REPORT.md) · [반복 측정 원문](evaluation/results/comparison/repeats.json) · [검색 부담 원문](evaluation/results/comparison/retrieval-overhead.json)

## 6. 한계와 트레이드오프

- 문서 6개·질문 20개의 작은 교육용 데이터다. 평가용 6개는 검색 기준을 조정하는 데 사용하지 않았지만 이미 관측한 시험 세트이므로 새로운 독립 검증 데이터가 필요하다. 운영 환경의 정확도나 통계적 유의성을 주장하지 않는다.
- 단일 시점 모의 지표와 알림만 있다. 실제 로그·배포·시계열·서비스 의존 관계가 없어 근본 원인·공통 원인·복구를 확정하지 않는다.
- RAG 초기 테스트에서 영어 알림과 한국어 문서의 검색 오류가 있어 한·영 증상 설명을 보강했다. 유사도는 정답 확률이 아니며 미지원 장애의 검색 거절, 같은 서비스의 복합 장애는 추가 검증이 필요하다.
- 원문 기반 출력은 조건 변형을 줄이는 대신 자유로운 종합 설명의 범위를 제한한다. 문서가 잘못되거나 오래되면 이 검증만으로 해결할 수 없다. 실제 조치의 조건 충족 여부를 자동 판정·실행하지 않는다.
- 검증 후 전송하므로 장애 답변의 초안을 즉시 보여주지 않는다. 시간·생성량 제한은 긴 대기를 줄이지만 E06처럼 안내 응답으로 끝날 수 있다.
- 대상은 등록 목록을 기준으로 제한한다. 오타·새 별칭·알 수 없는 서비스는 추가 확인이 필요하며 자율적인 조사 대상 확장은 지원하지 않는다.
- SQLite 전수 벡터 비교를 사용했다. 대규모 검색·동시 사용자 부하·OpenAI 백엔드는 검증 범위 밖이다.

## 7. 검증 결과

- 단위 테스트 31개: 누락·미등록·정상·부분 실패·조회 시간 초과·잘못된 수치·원인 확정·없는 절차·이름 질문·전체 요청 제한 확인
- 실제 MCP·프록시·SSE: 10개 시나리오의 11개 요청에서 대상·문서·종료·최종 내용 일치 확인
- 의도적 최초 모니터링 실패: 재시도 1회 후 복구
- SQLite: 새 서버 PID에서 같은 DB·thread를 유지한 뒤 사용자 이름을 올바르게 응답
- 실행 스크립트: 기존 포트 사용 중이면 중단하며 프로세스·DB 유지
- 원본 47개 파일 해시 보존, 평가 데이터와 지표 검사 통과

초기 통합 검증에서는 이름 질문을 새 선언으로 읽는 오류를 발견했다. 선언에 종결 표현을 요구하도록 수정하고 회귀 테스트를 추가한 뒤 전체 평가와 통합 검증을 다시 실행했다. 첫 실패 기록은 로컬에 보존했다.

[실행·평가 재현](docs/REPRODUCE.md) · [원본과 변경 모듈](docs/CHANGES.md) · [단위 테스트 결과](evaluation/test-results/unit-tests.txt)

발표자료는 표지 포함 35장으로, 기존 질문의 문제와 개선 코드·실행 결과, 추가 기능과 평가 결과를 담았다.
'''
(ROOT/'REPORT.md').write_text(md)
print('Report generated from saved results.')
