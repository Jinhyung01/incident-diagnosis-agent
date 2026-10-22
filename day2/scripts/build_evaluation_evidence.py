"""Render evaluation criteria and case evidence from preserved execution records."""

import html
import json
import statistics
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / "day2/results/comparison"
before = json.loads((R / "day1/results/baseline-ollama/results.json").read_text())
after = json.loads((R / "day2/results/improved-ollama/results.json").read_text())
bmap = {r["id"]: r for r in before}
amap = {r["id"]: r for r in after}
assert bmap.keys() == amap.keys()
for key in ["dataset_sha256", "fixture_sha256", "fast_model", "quality_model"]:
    b = json.loads((R / "day1/results/baseline-ollama/config.json").read_text())
    a = json.loads((R / "day2/results/improved-ollama/config.json").read_text())
    assert b[key] == a[key]
paired = [k for k in bmap if not bmap[k]["error"] and not amap[k]["error"]]


def ratio(records, key, den):
    return f"{sum(r['metrics'][key] for r in records)}/{sum(r['metrics'][den] for r in records)}"


def select(records):
    x = [r for r in records if r["metrics"]["runbook_top1_correct"] is not None]
    return f"{sum(r['metrics']['runbook_top1_correct'] for r in x)}/{len(x)}"


rows = [
    (
        "필요한 서비스 수집",
        "질문에 필요한 등록 서비스와 실제 조회 목록 대조",
        ratio(before, "matched_targets", "expected_target_count"),
        ratio(after, "matched_targets", "expected_target_count"),
    ),
    (
        "조회 범위 일치",
        "누락·불필요한 대체 조회가 모두 없는 질문 수",
        f"{sum(r['metrics']['target_scope_pass'] for r in before)}/20",
        f"{sum(r['metrics']['target_scope_pass'] for r in after)}/20",
    ),
    (
        "매뉴얼 첫 선택 일치",
        "정답 문서가 1개인 질문 12개의 첫 선택 대조",
        select(before),
        select(after),
    ),
    (
        "처리 시간 중앙값",
        f"양쪽 완료한 동일 {len(paired)}개 질문의 그래프 실행 시간",
        f"{statistics.median(bmap[k]['elapsed_seconds'] for k in paired):.2f}초",
        f"{statistics.median(amap[k]['elapsed_seconds'] for k in paired):.2f}초",
    ),
    (
        "최종 응답 반환",
        "실행 예외 없이 응답 반환, 확인·실패 안내 포함",
        f"{sum(not r['error'] for r in before)}/20",
        f"{sum(not r['error'] for r in after)}/20",
    ),
]
css = """body{font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;color:#172e40;margin:0;padding:28px 34px;background:white;line-height:1.45}h1{font-size:30px;margin:0 0 9px}p{font-size:17px;margin:8px 0 17px}table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:24px}th,td{border-bottom:1px solid #d8e2e6;padding:13px 13px;text-align:left;vertical-align:top}th{background:#17394c;color:white}.note{font-size:16px;color:#465c6a;margin-top:17px}.id{font-weight:700;color:#12786d}small{font-size:15px;color:#465c6a}a{color:#12786d}td:nth-last-child(-n+2){font-weight:600}"""


def page(title, body):
    return f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>{title}</title><style>{css}</style><main>{body}</main></html>'


esc = html.escape
trs = "".join(
    "<tr>" + "".join("<td>" + esc(v) + "</td>" for v in row) + "</tr>" for row in rows
)
summary = f"""<h1>동일 질문 20개 비교 결과</h1><p>고정 모니터링 지표 · 같은 qwen3:0.6b / 8b · 질문별 1회 · 질문마다 대화 분리</p><table><colgroup><col style="width:23%"><col style="width:49%"><col style="width:14%"><col style="width:14%"></colgroup><tr><th>측정 항목</th><th>판정 기준</th><th>개선 전</th><th>개선 후</th></tr>{trs}</table><p class="note">실제 모델·그래프 실행 기록 집계. 고정 데이터 어댑터 사용, 네트워크 전송·화면 표시·워밍업·인덱스 구축 시간 제외.<br>생성 설정·출력 형식·처리 단계도 변경. RAG 단독 효과 또는 전체 답변 정확도 평가가 아님.<br>개선 후 20건: 검증 통과 13 · 관측/확인 안내 4 · 대화 2 · 검증 실패 안내 1</p>"""
(OUT / "evidence.html").write_text(page("측정 기준과 결과", summary))
changes = []
for cid in ["D05", "D06", "D07"]:
    b, a = bmap[cid], amap[cid]
    q = b["turns"][0]["query"]
    assert q == a["turns"][0]["query"]

    def label(r):
        m = r["metrics"]
        return (
            "조회: "
            + (", ".join(m["actual_targets"]) or "없음")
            + "<br>문서: "
            + (", ".join(m["actual_runbooks"]) or "없음")
        )

    changes.append(
        f'<tr><td><span class="id">{cid}</span> {esc(q)}</td><td>{label(b)}</td><td>{label(a)}</td></tr>'
    )
body = (
    '<h1>무엇이 달라졌는가</h1><p>동일 질문의 실제 조회·매뉴얼 기록을 비교</p><table><colgroup><col style="width:42%"><col style="width:29%"><col style="width:29%"></colgroup><tr><th>질문</th><th>개선 전</th><th>개선 후</th></tr>'
    + "".join(changes)
    + '</table><p class="note">D05·D06·D07: 빠진 서비스 3개 조사 보완. D07: db-down 대신 high-latency 선택.<br></p>'
)
(OUT / "cases.html").write_text(page("사례별 개선 증거", body))
print(
    "Generated evidence.html and cases.html directly from 40 preserved records; no model benchmark rerun."
)
