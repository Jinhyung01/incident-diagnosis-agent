"""Build chart data from preserved before/after runs without calling a model."""

import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    "day1/results/baseline-ollama/results.json",
    "day2/results/improved-ollama/results.json",
]
before, after = [json.loads((ROOT / f).read_text()) for f in SOURCES]
by_id = [{r["id"]: r for r in runs} for runs in [before, after]]
assert by_id[0].keys() == by_id[1].keys(), "Before/after questions differ"
paired = [
    case_id
    for case_id in by_id[0]
    if all(not runs[case_id]["error"] for runs in by_id)
]
assert paired, "No shared completed questions for timing comparison"
for key in ["dataset_sha256", "fixture_sha256", "fast_model", "quality_model"]:
    configs = [
        json.loads((ROOT / Path(f).parent / "config.json").read_text())
        for f in SOURCES
    ]
    assert configs[0][key] == configs[1][key], key


def count(runs, key):
    return sum(r["metrics"][key] for r in runs)


charts = []
denominators = [count(runs, "expected_target_count") for runs in [before, after]]
assert denominators[0] == denominators[1]
for title, key, denominator, criterion in [
    (
        f"필요한 서비스 수집 · 총 {denominators[0]}개",
        "matched_targets",
        denominators[0],
        "필요한 등록 서비스와 실제 조회 목록을 대조",
    ),
    (
        f"조회 범위 일치 · 총 {len(before)}문항",
        "target_scope_pass",
        len(before),
        "누락과 불필요한 대체 조회가 모두 없는 질문 수",
    ),
]:
    values = [count(runs, key) for runs in [before, after]]
    charts.append(
        {
            "title": title,
            "values": values,
            "labels": [f"{v}/{denominator}" for v in values],
            "max": denominator * 1.25,
            "criterion": criterion,
        }
    )
single = [
    [r for r in runs if r["metrics"]["runbook_top1_correct"] is not None]
    for runs in [before, after]
]
assert {r["id"] for r in single[0]} == {r["id"] for r in single[1]}
denominator = len(single[0])
values = [count(runs, "runbook_top1_correct") for runs in single]
charts.append(
    {
        "title": f"매뉴얼 선택 · 정답 1개인 {denominator}문항",
        "values": values,
        "labels": [f"{v}/{denominator}" for v in values],
        "max": denominator * 1.25,
        "criterion": "첫 선택 문서가 기대 문서와 같은 질문 수",
    }
)
times = [
    statistics.median(runs[case_id]["elapsed_seconds"] for case_id in paired)
    for runs in by_id
]
charts.append(
    {
        "title": f"처리 시간 중앙값 · 같은 {len(paired)}문항",
        "values": times,
        "labels": [f"{value:.2f}초" for value in times],
        "max": math.ceil(max(times) * 1.3),
        "criterion": "전후 모두 완료한 같은 질문의 그래프 실행 시간",
    }
)
metrics = {
    "charts": charts,
    "paired_case_ids": paired,
    "source_sha256": {
        f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in SOURCES
    },
    "limits": [
        "같은 질문·고정 지표·모델 사용",
        "생성 설정·분기·출력 형식도 변경",
        "시간은 UI·통신·워밍업·인덱스 구축 제외",
        "새 모델 평가 실행이 아닌 보존 기록의 재집계",
    ],
}
quality_denominators = [denominators[0], len(before), denominator]
quality_counts = [
    [charts[index]["values"][side] for index in range(3)] for side in range(2)
]
metrics["quality"] = {
    "categories": ["서비스 조회", "조회 대상 일치", "매뉴얼 선택"],
    "denominators": quality_denominators,
    "counts": quality_counts,
    "series": [
        {
            "name": name,
            "values": [
                round(value / total, 4)
                for value, total in zip(counts, quality_denominators)
            ],
        }
        for name, counts in zip(["개선 전", "개선 후"], quality_counts)
    ],
    "scope": "등록 서비스 조회·대상 집합·단일 정답 매뉴얼 첫 선택의 일치율",
    "service_count_definition": "요청별 필요한 등록 대상의 합계. 같은 서비스가 다른 질문에 나오면 다시 계수한다.",
    "semantic_diagnosis_accuracy_measured": False,
    "timing_is_secondary": True,
}
output = ROOT / "day2/results/comparison/presentation-metrics.json"
output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
print("Generated four chart datasets from preserved execution records.")
