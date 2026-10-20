"""Validate evaluation fixtures, metric edge cases, and baseline preservation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from run_baseline import FixedMCP, score
import asyncio

ROOT = Path(__file__).resolve().parents[2]
DAY1 = ROOT / "day1"


def read(path):
    return json.loads(path.read_text())


async def main():
    manifest = read(DAY1 / "baseline/manifest.json")
    snapshot = DAY1 / "baseline/original_v2"
    for entry in manifest["files"]:
        content = (snapshot / entry["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == entry["snapshot_sha256"], entry["path"]
        if not entry["credential_template_redacted"]:
            live = (ROOT / "all_total_vue_student" / entry["path"]).read_bytes()
            assert hashlib.sha256(live).hexdigest() == entry["source_sha256"], entry["path"]

    cases = read(DAY1 / "evaluation/cases.json")["cases"]
    fixtures = read(DAY1 / "evaluation/fixtures.json")
    monitoring = read(snapshot / "data/monitoring.json")
    books = {p.stem for p in (snapshot / "data/runbooks").glob("*.md")}
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids)) == 20
    for case in cases:
        assert set(case["expected_targets"]) <= set(monitoring)
        assert set(case["expected_runbooks"]) <= books
        assert case["scenario"] in fixtures["scenarios"]
        assert bool(case.get("query")) != bool(case.get("messages"))

    adapter = FixedMCP(snapshot, fixtures, "cpu_boundary")
    result = await adapter.call_tool("get_monitoring_status", {"system_name": "payments-service"})
    assert result["cpu_percent"] == 89.1
    fresh = FixedMCP(snapshot, fixtures, "base")
    base_result = await fresh.call_tool("get_monitoring_status", {"system_name": "payments-service"})
    assert base_result["cpu_percent"] == 91.0, "Scenario leaked into another case"
    assert result["last_checked"] == base_result["last_checked"]

    # Unknown-target tests have no recall denominator, but still fail unexpected lookup.
    unknown = next(c for c in cases if c["id"] == "D08")
    m = score(unknown, fresh.calls, {"final": ""})
    assert m["target_recall"] is None and not m["target_scope_pass"]
    # Zero expected documents is not silently counted as 100% retrieval recall.
    assert m["runbook_recall"] is None
    multiple = next(c for c in cases if c["id"] == "D06")
    m = score(multiple, fresh.calls, {"final": ""})
    assert m["target_recall"] == 0.5 and m["missing_targets"] == ["cache-service"]
    retry = FixedMCP(snapshot, fixtures, "base", flaky=True)
    try:
        await retry.call_tool("get_monitoring_status", {"system_name": "payments-service"})
        raise AssertionError("Expected simulated transient failure")
    except asyncio.TimeoutError:
        pass
    await retry.call_tool("get_monitoring_status", {"system_name": "payments-service"})
    print("PASS: 47 snapshot hashes, unchanged source code, 20 case contracts, fixture isolation, metric edge cases, retry control.")


if __name__ == "__main__":
    asyncio.run(main())
