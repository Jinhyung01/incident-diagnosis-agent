"""Measure index build and warm search overhead separately from chat timing."""

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "all_total_vue_student"))
from agent.retrieval import RunbookRetriever

QUERIES = [
    "CPU 91% (threshold 80%); instance responding slow",
    "memory usage climbing steadily over 6h; heap near limit",
    "disk usage 95% on /var/log; disk space low",
    "upstream timeout (504); network packet loss 3%",
    "p95 latency 2.4s; connection pool 92% used",
]
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        r = RunbookRetriever(
            ROOT / "all_total_vue_student/data/runbooks", Path(tmp) / "index.sqlite"
        )
        started = time.perf_counter()
        build = r.build()
        build_seconds = time.perf_counter() - started
        searches = []
        for repeat in range(3):
            for q in QUERIES:
                started = time.perf_counter()
                result = r.search("상태 degraded. 증상: " + q)
                searches.append(
                    {
                        "query": q,
                        "repeat": repeat + 1,
                        "seconds": round(time.perf_counter() - started, 6),
                        "top1": result["matches"][0]["id"]
                        if result["matches"]
                        else None,
                    }
                )
    target = ROOT / "evaluation/results/comparison/retrieval-overhead.json"
    target.write_text(
        json.dumps(
            {
                "build_seconds": round(build_seconds, 6),
                "build": build,
                "note": "로컬 Ollama 실행 중, 이미 설치된 모델과 OS 캐시를 사용한 소규모 측정. 다운로드·서버 시작 시간 제외.",
                "searches": searches,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print("Build seconds", build_seconds, "searches", len(searches))
