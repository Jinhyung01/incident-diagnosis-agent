"""Run the unchanged v2 graph with a fixed-data MCP test adapter.

This is a graph/LLM evaluation, not an end-to-end MCP transport benchmark.
Real-model mode calls only the existing local Ollama endpoint. It does not
start/stop the user's servers, load .env, or write to the project's session DB.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import inspect
import json
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
DAY1 = ROOT / "day1"


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


class FixedMCP:
    """Same data capabilities as the baseline ops server, without transport."""
    def __init__(self, source: Path, fixture: dict, scenario: str, flaky=False):
        self.source = source
        # Freeze monitoring input independently of the implementation under test.
        self.data = read_json(DAY1 / "baseline/original_v2/data/monitoring.json")
        for target, values in fixture["scenarios"][scenario].items():
            self.data[target].update(copy.deepcopy(values))
        self.last_checked = fixture["last_checked"]
        self.calls = []
        self.flaky = flaky

    async def find_prompt(self, name):
        if name != "incident_analysis_prompt":
            raise ValueError(name)
        return "ops"

    async def get_prompt(self, name, arguments, server="ops"):
        if name != "incident_analysis_prompt" or server != "ops":
            raise ValueError(name)
        system = arguments["system_name"]
        symptom = arguments["symptom"]
        return f"""다음 장애에 대해 표준 진단 절차를 수행하세요.

## 장애 정보
- 시스템: {system}
- 증상: {symptom}

## 진단 절차 (반드시 순서대로 수행)
1. get_monitoring_status Tool로 관련 시스템의 현재 상태를 조회하세요.
2. 증상에 해당하는 runbook(runbook://incident-response/...)을 확인하세요.
3. 위 정보를 종합해 가능한 원인과 권장 조치를 제시하세요.
"""

    async def find_resource_template(self, name):
        if name != "get_incident_runbook":
            raise ValueError(name)
        return "ops", "runbook://incident-response/{incident_type}"

    async def call_tool(self, name, arguments, server="ops"):
        if name != "get_monitoring_status" or server != "ops":
            raise ValueError(name)
        if self.flaky:
            self.flaky = False
            self.calls.append({"kind": "transient_error", "target": arguments["system_name"]})
            raise asyncio.TimeoutError("Controlled evaluation timeout")
        target = arguments["system_name"]
        data = self.data.get(target)
        if data is None:
            result = {
                "system_name": target, "status": "unknown", "cpu_percent": 0.0,
                "memory_percent": 0.0, "last_checked": self.last_checked,
                "alerts": [f"System '{target}' not found in monitoring"],
            }
        else:
            result = {
                "system_name": target, "status": data["status"],
                "cpu_percent": data["cpu_base"], "memory_percent": data["memory_base"],
                "last_checked": self.last_checked, "alerts": list(data["alerts"]),
            }
        self.calls.append({"kind": "monitoring", "target": target, "result": result})
        return copy.deepcopy(result)

    async def read_resource(self, uri, server):
        prefix = "runbook://incident-response/"
        if not uri.startswith(prefix) or server != "ops":
            raise ValueError(uri)
        target = uri[len(prefix):]
        if "/" in target or ".." in target:
            raise ValueError(target)
        path = self.source / "data/runbooks" / f"{target}.md"
        body = path.read_text() if path.exists() else (
            f"# Runbook Not Found\n\nNo runbook for incident type: {target}"
        )
        self.calls.append({"kind": "runbook", "target": target, "found": path.exists()})
        return body


def instrument_usage(model, usages):
    # These methods return actual Ollama token counts or explicitly synthetic fake usage.
    for name in ("_chat", "_chat_stream"):
        if not hasattr(model, name):
            continue
        original = getattr(model, name)
        if inspect.iscoroutinefunction(original):
            async def wrapper(*args, _original=original, **kwargs):
                result = await _original(*args, **kwargs)
                usages.append({k: v for k, v in result[1].items() if k != "prompt"})
                return result
        else:
            def wrapper(*args, _original=original, **kwargs):
                result = _original(*args, **kwargs)
                usages.append({k: v for k, v in result[1].items() if k != "prompt"})
                return result
        setattr(model, name, wrapper)


def score(case, calls, result):
    expected = set(case["expected_targets"])
    actual = {c["target"] for c in calls if c["kind"] == "monitoring" and c["result"]["status"] != "unknown"}
    runbooks = list(dict.fromkeys(c["target"] for c in calls if c["kind"] == "runbook" and c["found"]))
    expected_books = set(case["expected_runbooks"])
    final = result.get("final", "")
    review_flags = []
    if "로그 분석 결과" in final or "로그를 분석한 결과" in final:
        review_flags.append("Possible unsupported log-analysis claim; human review required.")
    if "92% 초과" in final and case["id"] == "D04":
        review_flags.append("Possible 92% versus >92% mismatch; human review required.")
    return {
        "expected_targets": sorted(expected), "actual_targets": sorted(actual),
        "matched_targets": len(expected & actual), "expected_target_count": len(expected),
        "target_recall": len(expected & actual) / len(expected) if expected else None,
        "missing_targets": sorted(expected - actual), "unexpected_targets": sorted(actual - expected),
        "target_scope_pass": actual == expected,
        "expected_runbooks": sorted(expected_books), "actual_runbooks": runbooks,
        "runbook_recall": len(expected_books & set(runbooks)) / len(expected_books) if expected_books else None,
        "runbook_top1_correct": bool(runbooks and runbooks[0] in expected_books) if len(expected_books) == 1 else None,
        "runbook_none_pass": not runbooks if not expected_books else None,
        "runbook_scope_pass": set(runbooks) == expected_books,
        "route": result.get("route"), "review_flags": review_flags,
        "human_review_status": "pending",
        "human_review_checklist": case["review"],
        "note": "Automatic flags are screening hints, not a factuality score. Target scope assumes the defined evaluation policy.",
    }


async def run(args):
    source = args.source.resolve()
    sys.path.insert(0, str(source))
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGSMITH_TRACING"] = "false"
    sys.dont_write_bytecode = True
    from agent.deps import SupervisorDeps
    from agent.graph import build_graph

    cases = read_json(DAY1 / "evaluation/cases.json")["cases"]
    fixture = read_json(DAY1 / "evaluation/fixtures.json")
    if args.cases:
        requested = set(args.cases.split(","))
        unknown = requested - {c["id"] for c in cases}
        if unknown:
            raise ValueError(f"Unknown case IDs: {sorted(unknown)}")
        cases = [c for c in cases if c["id"] in requested]
    if args.split:
        cases = [c for c in cases if c["split"] == args.split]
    if not cases:
        raise ValueError("No selected cases")
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite results: {args.output}")
    args.output.mkdir(parents=True)

    config = {
        "created_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "source": str(source), "backend": args.backend,
        "fast_model": args.fast_model, "quality_model": args.quality_model,
        "case_ids": [c["id"] for c in cases], "repeat": args.repeat,
        "evaluation_mode": "unchanged graph + fixed-data MCP adapter",
        "actual_mcp_transport_tested": False,
        "session_storage": "in-memory isolated history; original SQLite untouched",
        "flaky_first_tool_call_per_case": args.flaky_first_tool_call,
        "fixture_sha256": hashlib.sha256((DAY1 / "evaluation/fixtures.json").read_bytes()).hexdigest(),
        "dataset_sha256": hashlib.sha256((DAY1 / "evaluation/cases.json").read_bytes()).hexdigest(),
        "sample_data_sha256": hashlib.sha256((DAY1 / "baseline/original_v2/data/monitoring.json").read_bytes()).hexdigest(),
        "temperature": 0, "timing": "graph invocation only; excludes warmup/index construction",
        "cost_note": "cost_usd is a synthetic comparison value, not an invoice.",
        "factuality": "Manual review required; automatic metrics cover target and runbook selection.",
    }
    if args.backend == "ollama":
        from agent.ollama_llm import OllamaFastLLM, OllamaQualityLLM
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as resp:
            all_models = json.load(resp)["models"]
        names = {m["name"] for m in all_models}
        if {args.fast_model, args.quality_model} - names:
            raise RuntimeError("Required local models are not installed")
        config["model_metadata"] = [m for m in all_models if m["name"] in {args.fast_model, args.quality_model}]
        for model in dict.fromkeys([args.fast_model, args.quality_model]):
            print(f"Warmup: {model}", flush=True)
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=json.dumps({"model": model, "prompt": "hi", "stream": False,
                                 "options": {"num_predict": 1, "temperature": 0}}).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp.read()
        fast = OllamaFastLLM(args.fast_model, 0.00015)
        quality = OllamaQualityLLM(args.quality_model, 0.005)
    else:
        from agent.fake_llm import FastLLM, QualityLLM
        fast, quality = FastLLM("fake-fast", 0.00015), QualityLLM("fake-quality", 0.005)
    write_json(args.output / "config.json", config)
    usages = []
    instrument_usage(fast, usages)
    instrument_usage(quality, usages)
    outcomes = []
    for repeat in range(1, args.repeat + 1):
        for case in cases:
            print(f"START {case['id']} repeat={repeat}", flush=True)
            adapter = FixedMCP(source, fixture, case["scenario"], args.flaky_first_tool_call)
            deps = SupervisorDeps(fast, quality, adapter, None, "v2")
            graph = build_graph(deps)
            history, turns = [], []
            usages.clear()
            for query in case.get("messages", [case.get("query")]):
                start = time.perf_counter()
                error, result = None, {}
                try:
                    result = await graph.ainvoke({
                        "query": query, "thread_id": f"eval-{case['id']}-{repeat}",
                        "history": copy.deepcopy(history), "events": [], "cost_usd": 0.0,
                    })
                    history.extend([{"role": "user", "content": query},
                                    {"role": "assistant", "content": result["final"]}])
                except Exception as exc:
                    error = {"type": type(exc).__name__, "message": str(exc)}
                turns.append({"query": query, "elapsed_seconds": round(time.perf_counter() - start, 3),
                              "error": error, "result": result})
                if error:
                    break
            final = turns[-1]["result"]
            outcome = {
                "id": case["id"], "repeat": repeat, "split": case["split"],
                "category": case["category"], "scenario": case["scenario"],
                "expected_behavior": case["expected_behavior"], "turns": turns,
                "calls": adapter.calls, "usage": copy.deepcopy(usages),
                "tokens": sum(u.get("tokens", 0) for u in usages) if args.backend == "ollama" else None,
                "elapsed_seconds": round(sum(t["elapsed_seconds"] for t in turns), 3),
                "error": any(t["error"] for t in turns),
                "metrics": score(case, adapter.calls, final),
            }
            outcomes.append(outcome)
            write_json(args.output / f"{case['id']}-r{repeat}.json", outcome)
            write_json(args.output / "results.json", outcomes)
            m = outcome["metrics"]
            print(f"DONE {case['id']} time={outcome['elapsed_seconds']}s "
                  f"targets={m['actual_targets']} runbooks={m['actual_runbooks']} "
                  f"error={outcome['error']}", flush=True)
    print(f"Saved {len(outcomes)} cases to {args.output}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=DAY1 / "baseline/original_v2")
    p.add_argument("--backend", choices=["fake", "ollama"], default="fake")
    p.add_argument("--fast-model", default="qwen3:0.6b")
    p.add_argument("--quality-model", default="qwen3:8b")
    p.add_argument("--cases", help="Comma-separated IDs, e.g. D06,D08,M02")
    p.add_argument("--split", choices=["development", "evaluation", "supplemental"])
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--flaky-first-tool-call", action="store_true")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.repeat < 1:
        p.error("--repeat must be positive")
    asyncio.run(run(args))
