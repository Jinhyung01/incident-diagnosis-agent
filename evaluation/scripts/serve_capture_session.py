"""Observe genuine model calls and SSE results for contextual presentation captures.

No model answers are supplied or replaced. All production logic is imported unchanged.
Each request is saved under a unique record name; the private SQLite DB is separate.
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "all_total_vue_student"
OUT = ROOT / "evaluation/results/contextual-captures"
parser = argparse.ArgumentParser()
parser.add_argument("--proxy", action="store_true")
args = parser.parse_args()
sys.path.insert(0, str(SOURCE))
os.environ.update(
    LLM_BACKEND="ollama",
    MONITORING_FIXED="true",
    PROJECT_TRACING="false",
    PYTHONDONTWRITEBYTECODE="1",
    SESSION_DB_PATH=str(ROOT / "evaluation/runtime/contextual-captures/session.db"),
    BACKEND_URL="http://127.0.0.1:8206",
)
import uvicorn

if args.proxy:
    import web_demo_server

    uvicorn.run(web_demo_server.app, host="127.0.0.1", port=8706)
else:
    import server

    OUT.mkdir(parents=True, exist_ok=True)
    original_build = server.build_graph
    original_execute = server.execute
    model_calls = []

    class ObservedReport:
        def __init__(self, delegate):
            self.delegate = delegate
            self.name = delegate.name

        async def write(self, query, *rest, **kwargs):
            draft, usage = await self.delegate.write(query, *rest, **kwargs)
            model_calls.append(
                {"query": query, "attempt": rest[1], "raw_model_output": draft, "usage": usage}
            )
            return draft, usage

    def build(deps):
        deps.quality_llm = ObservedReport(deps.quality_llm)
        return original_build(deps)

    async def record(message, thread_id):
        before = len(model_calls)
        events = []
        async for event in original_execute(message, thread_id):
            events.append(event)
            yield event
        target = OUT / f"{thread_id}-{uuid4().hex[:8]}.json"
        with target.open("x") as out:
            json.dump(
                {
                    "captured_at": datetime.now(UTC).isoformat(),
                    "thread_id": thread_id,
                    "query": message,
                    "model_calls": model_calls[before:],
                    "events": events,
                    "data_control": "Original base monitoring values, jitter=0",
                    "answer_replayed_or_replaced": False,
                },
                out,
                ensure_ascii=False,
                indent=2,
            )
            out.write("\n")

    server.build_graph = build
    server.execute = record
    uvicorn.run(server.app, host="127.0.0.1", port=8206)
