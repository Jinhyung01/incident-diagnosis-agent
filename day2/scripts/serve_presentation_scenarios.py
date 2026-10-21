"""Capture real UI failure paths with a controlled fixture and delayed dependency.

This wrapper does not replace answers. web-01 has degraded status without alerts;
payments requests delay the report dependency for 30s under an 8s request budget.
The production defaults remain 60s/request and 25s/call.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "all_total_vue_student"
OUT = ROOT / "day2/results/presentation-scenarios"
RUNTIME = ROOT / "day2/runtime/presentation-scenarios"
parser = argparse.ArgumentParser()
parser.add_argument("--proxy", action="store_true")
args = parser.parse_args()
sys.path.insert(0, str(SOURCE))
os.environ.update(
    LLM_BACKEND="ollama",
    MONITORING_FIXED="true",
    PROJECT_TRACING="false",
    PYTHONDONTWRITEBYTECODE="1",
    SESSION_DB_PATH=str(RUNTIME / "session.db"),
    REQUEST_TIMEOUT_SECONDS="8",
    BACKEND_URL="http://127.0.0.1:8205",
)
import uvicorn

if args.proxy:
    import web_demo_server

    uvicorn.run(web_demo_server.app, host="127.0.0.1", port=8705)
else:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = json.loads((SOURCE / "data/monitoring.json").read_text())
    fixture["web-01"].update(status="degraded", alerts=[])
    fixture_path = OUT / "monitoring-fixture.json"
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n")
    os.environ["MONITORING_FIXTURE_PATH"] = str(fixture_path)
    import server

    original_build = server.build_graph
    original_execute = server.execute

    class DelayedReport:
        def __init__(self, delegate):
            self.delegate = delegate
            self.name = delegate.name

        async def write(self, query, *rest, **kwargs):
            if "payments-service" in query:
                await asyncio.sleep(30)
            return await self.delegate.write(query, *rest, **kwargs)

    def build(deps):
        deps.quality_llm = DelayedReport(deps.quality_llm)
        return original_build(deps)

    async def record(message, thread_id):
        events = []
        async for event in original_execute(message, thread_id):
            events.append(event)
            yield event
        key = (
            "unknown"
            if "billing-service" in message
            else "timeout"
            if "payments-service" in message
            else "insufficient"
        )
        (OUT / f"{key}.json").write_text(
            json.dumps(
                {
                    "query": message,
                    "controlled_test": True,
                    "fixture": "monitoring-fixture.json",
                    "request_timeout_seconds": 8,
                    "injected_report_delay_seconds": 30 if key == "timeout" else 0,
                    "events": events,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )

    server.build_graph = build
    server.execute = record
    uvicorn.run(server.app, host="127.0.0.1", port=8205)
