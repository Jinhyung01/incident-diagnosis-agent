"""Summarize paired fixed-data results without treating fallback as validated success."""

import html
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "day2/results/comparison"
OUT.mkdir(parents=True, exist_ok=True)


def read(p):
    return json.loads(p.read_text())


def summarize(records):
    good = [r for r in records if not r["error"]]
    return {
        "cases": len(records),
        "completed": len(good),
        "targets_matched": sum(r["metrics"]["matched_targets"] for r in records),
        "targets_expected": sum(r["metrics"]["expected_target_count"] for r in records),
        "target_scope": sum(r["metrics"]["target_scope_pass"] for r in records),
        "top1": sum(r["metrics"]["runbook_top1_correct"] is True for r in records),
        "single_cases": sum(
            r["metrics"]["runbook_top1_correct"] is not None for r in records
        ),
        "none_pass": sum(r["metrics"]["runbook_none_pass"] is True for r in records),
        "none_cases": sum(
            r["metrics"]["runbook_none_pass"] is not None for r in records
        ),
        "median_success_seconds": round(
            statistics.median(r["elapsed_seconds"] for r in good), 3
        ),
    }


before_dir = ROOT / "day1/results/baseline-ollama"
after_dir = ROOT / "day2/results/improved-ollama"
before = read(before_dir / "results.json")
after = read(after_dir / "results.json")
bcfg = read(before_dir / "config.json")
acfg = read(after_dir / "config.json")
for key in [
    "fixture_sha256",
    "dataset_sha256",
    "fast_model",
    "quality_model",
    "sample_data_sha256",
]:
    assert bcfg[key] == acfg[key], key
bmap = {r["id"]: r for r in before}
amap = {r["id"]: r for r in after}
assert bmap.keys() == amap.keys()
paired = [id for id in bmap if not bmap[id]["error"] and not amap[id]["error"]]
status = dict(
    Counter(r["turns"][-1]["result"].get("answer_status", "unknown") for r in after)
)
summary = {
    "before": summarize(before),
    "after": summarize(after),
    "after_answer_status": status,
    "paired_completed_cases": len(paired),
    "paired_median_before_seconds": round(
        statistics.median(bmap[id]["elapsed_seconds"] for id in paired), 3
    ),
    "paired_median_after_seconds": round(
        statistics.median(amap[id]["elapsed_seconds"] for id in paired), 3
    ),
    "dataset_sha256": acfg["dataset_sha256"],
    "fixture_sha256": acfg["fixture_sha256"],
    "limitations": [
        "질문별 1회, 20개 교육용 사례",
        "개선 후 구조화 생성·think=false·512토큰 상한·시간 제한 적용; RAG만의 인과 효과가 아님",
        "안내 응답도 최종 응답 완료에 포함",
        "실제 MCP 전송·UI는 별도 통합 시험",
    ],
}
(OUT / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
)
b = summary["before"]
a = summary["after"]
rows = [
    ("최종 응답 완료", f"{b['completed']}/20", f"{a['completed']}/20"),
    (
        "요청한 등록 대상 수집",
        f"{b['targets_matched']}/{b['targets_expected']}",
        f"{a['targets_matched']}/{a['targets_expected']}",
    ),
    ("조회 대상 범위 일치", f"{b['target_scope']}/20", f"{a['target_scope']}/20"),
    (
        "단일 정답 매뉴얼 Top-1",
        f"{b['top1']}/{b['single_cases']}",
        f"{a['top1']}/{a['single_cases']}",
    ),
    (
        "불필요한 매뉴얼 검색 생략",
        f"{b['none_pass']}/{b['none_cases']}",
        f"{a['none_pass']}/{a['none_cases']}",
    ),
    (
        "성공 응답 시간 중앙값",
        f"{b['median_success_seconds']:.2f}초 (16건)",
        f"{a['median_success_seconds']:.2f}초 (20건)",
    ),
]
md = [
    "# 고정 데이터 개선 전후 비교",
    "",
    "동일한 원본 v2 기준 질문 20개·고정 모니터링 데이터·qwen3:0.6b/8b를 사용했다. 각 질문의 세션을 분리했고 일반 대화 보조 사례 2개를 포함한다. 실제 MCP 전송 대신 데이터 어댑터를 사용한 그래프 평가다.",
    "",
    "| 지표 | 개선 전 | 개선 후 |",
    "|---|---:|---:|",
]
md += ["| " + " | ".join(row) + " |" for row in rows]
md += [
    "",
    f"개선 후 응답 구성: 구조화 검증 통과 {status.get('validated', 0)}건, 관측·대상 확인 안내 {status.get('observation', 0)}건, 일반 대화 {status.get('chat', 0)}건, 생성·검증 실패 후 안내 {status.get('fallback', 0)}건.",
    "",
    "E06(등록·미등록 혼합 요청)은 두 번의 생성에서도 서비스 범위를 벗어난 필드가 남아 검증에 실패했다. 강제로 통과시키지 않고 실제 payments 관측과 매뉴얼 원문, billing 미등록 안내를 반환했다. 응답 완료가 모든 LLM 초안의 성공을 뜻하지 않는다.",
    "",
    f"양쪽 모두 완료한 {len(paired)}건만 비교하면 중앙값은 {summary['paired_median_before_seconds']:.2f}초 → {summary['paired_median_after_seconds']:.2f}초다.",
    "",
    "## 비교 조건과 해석",
    "",
    "- 모델 이름·평가 데이터 해시는 일치한다. 개선 전 원본은 think/생성량 제한 설정이 없고 호출 읽기 제한이 300초다.",
    "- 개선 후 think=false, 생성 512토큰 상한, 호출 25초·전체 요청 60초 상한, 최대 작성 2회를 적용했다. 사고·답변 형식과 작업 단계도 바뀌었다.",
    "- 생성량·분기·출력 형식 변경이 지연 차이에 함께 영향을 줬다. RAG 또는 모델 성능만의 효과로 해석하지 않는다.",
    "- 검색은 기존 6개 매뉴얼 본문에 한·영 증상 설명을 보강해 임베딩했다. 데이터 보강과 RAG가 함께 바뀌었다.",
    "- 6개 문서·20개 질문에서 얻은 값이며 운영 환경의 정확도나 통계적 유의성을 뜻하지 않는다.",
    "- 같은 입력 중 원래 auth 기본 처리를 기대했던 항목은 이번 정책의 대상 확인 동작을 기준으로 평가한다.",
    "- 시간 초과 호출의 토큰 사용량은 누락될 수 있다. 원본 가상 비용을 실제 절감액으로 제시하지 않는다.",
    "",
    "## 사례별 결과",
    "",
    "| ID | 개선 전 조회 | 개선 후 조회 | 전/후 매뉴얼 | 전/후 시간(초) | 후 응답 유형 |",
    "|---|---|---|---|---:|---|",
]
for id in bmap:
    x, y = bmap[id], amap[id]
    xm, ym = x["metrics"], y["metrics"]
    md.append(
        f"| {id} | {', '.join(xm['actual_targets']) or '없음'} | {', '.join(ym['actual_targets']) or '없음'} | {','.join(xm['actual_runbooks']) or '없음'} / {','.join(ym['actual_runbooks']) or '없음'} | {x['elapsed_seconds']:.2f}{' 실패' if x['error'] else ''} / {y['elapsed_seconds']:.2f} | {y['turns'][-1]['result'].get('answer_status')} |"
    )
(OUT / "REPORT.md").write_text("\n".join(md) + "\n")
esc = html.escape
trs = "".join(
    "<tr>" + "".join("<td>" + esc(v) + "</td>" for v in row) + "</tr>" for row in rows
)
page = f"""<!doctype html><html lang="ko"><meta charset="utf-8"><title>개선 전후 비교</title><style>body{{font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;background:#f1f5f7;color:#172b3f;margin:0;padding:45px;line-height:1.6}}main{{max-width:1120px;margin:auto}}h1{{font-size:34px}}table{{border-collapse:collapse;width:100%;background:white;font-size:21px}}th,td{{padding:17px 20px;border-bottom:1px solid #d9e2e9;text-align:left}}th{{background:#17394d;color:white}}p{{font-size:16px}}.note{{font-size:14px;color:#526779}}</style><main><p>AI Mini-project · 고정 데이터 20개 · 원본 v2 기준</p><h1>같은 질문·데이터로 개선 전후 비교</h1><table><tr><th>지표</th><th>개선 전</th><th>개선 후</th></tr>{trs}</table><p>개선 후: 검증 통과 13 · 관측/확인 안내 4 · 일반 대화 2 · 검증 실패 후 안내 1</p><p class="note">응답 완료에는 안내 응답도 포함합니다. 모델은 같지만 생성 설정·답변 형식·처리 단계가 바뀌었습니다. 실제 MCP·UI는 별도 통합 검증이며, 위 화면은 측정 기록을 정리한 비교 화면입니다.</p><p class="note">양쪽 모두 완료한 16건 중앙값: {summary["paired_median_before_seconds"]:.2f}초 → {summary["paired_median_after_seconds"]:.2f}초 · 6개 문서의 소규모 평가</p></main></html>"""
(OUT / "index.html").write_text(page)
print(json.dumps(summary, ensure_ascii=False))
