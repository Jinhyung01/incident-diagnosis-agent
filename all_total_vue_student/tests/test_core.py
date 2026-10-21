import asyncio
import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent.targets import select_targets, remembered_name
from agent.research import collect_monitoring, collect_runbooks
from agent.evidence import render_report, monitoring_state, runbook_steps
from agent.validation import validate_draft
from agent.retrieval import RunbookRetriever, normalize
from agent.deps import SupervisorDeps
from agent.graph import build_graph

CATALOG = set(json.loads((ROOT / "data/monitoring.json").read_text()))
BODY = (ROOT / "data/runbooks/cpu-spike.md").read_text()
MON = {
    "system_name": "payments-service",
    "status": "degraded",
    "cpu_percent": 89.1,
    "memory_percent": 54.1,
    "alerts": ["CPU 91% (threshold 80%)"],
    "last_checked": "2026-10-20T10:00:00+09:00",
}
COL = [
    {"source": "monitoring", "data": MON},
    {
        "source": "runbook",
        "service": "payments-service",
        "data": {
            "id": "cpu-spike",
            "title": "CPU 급증",
            "body": BODY,
            "uri": "runbook://incident-response/cpu-spike",
        },
    },
]
VALID = {
    "sections": [
        {
            "system_name": "payments-service",
            "cpu_percent": 89.1,
            "memory_percent": 54.1,
            "runbook_id": "cpu-spike",
            "step_ids": [1, 3],
            "cause_confirmed": False,
        }
    ]
}


class ScopeTests(unittest.TestCase):
    def test_all_three_regressions(self):
        for query, want in [
            (
                "gateway-service에서 payments-service로 타임아웃",
                ["gateway-service", "payments-service"],
            ),
            ("web-01 CPU, auth-service도", ["web-01", "auth-service"]),
            (
                "payments-service랑 cache-service 비교",
                ["payments-service", "cache-service"],
            ),
        ]:
            self.assertEqual(list(select_targets(query, CATALOG).known), want)

    def test_unknown_does_not_become_auth(self):
        s = select_targets("billing-service 응답이 느려요", CATALOG)
        self.assertEqual(s.known, ())
        self.assertEqual(s.unknown, ("billing-service",))

    def test_mixed_known_unknown(self):
        s = select_targets("payments-service와 billing-service", CATALOG)
        self.assertEqual(s.known, ("payments-service",))
        self.assertEqual(s.unknown, ("billing-service",))

    def test_unspecified_does_not_query(self):
        self.assertEqual(select_targets("로그인이 느려요", CATALOG).known, ())

    def test_boundaries_and_case(self):
        self.assertEqual(
            select_targets("web-010 PAYMENTS-SERVICE", CATALOG).known,
            ("payments-service",),
        )

    def test_user_name_only(self):
        history = [
            {"role": "assistant", "content": "제 이름은 철수입니다"},
            {"role": "user", "content": "제 이름은 민수입니다"},
        ]
        self.assertEqual(remembered_name(history), "민수")
        self.assertIsNone(remembered_name(history[:1]))

    def test_name_question_does_not_replace_declaration(self):
        history = [{"role": "user", "content": "제 이름은 민수입니다"}]
        self.assertEqual(remembered_name(history, "제 이름이 뭐였죠?"), "민수")
        self.assertIsNone(remembered_name([], "제 이름이 뭐였죠?"))


class ValidationTests(unittest.TestCase):
    def valid(self, d):
        return validate_draft(json.dumps(d), COL)[0]

    def test_accept_exact_evidence(self):
        self.assertTrue(self.valid(VALID))

    def test_reject_changed_cpu(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["cpu_percent"] = 91
        self.assertFalse(self.valid(d))

    def test_reject_other_service(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["system_name"] = "auth-service"
        self.assertFalse(self.valid(d))

    def test_reject_cause_confirmation(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["cause_confirmed"] = True
        self.assertFalse(self.valid(d))

    def test_reject_wrong_book(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["runbook_id"] = "memory-leak"
        self.assertFalse(self.valid(d))

    def test_reject_invented_step(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["step_ids"] = [90]
        self.assertFalse(self.valid(d))

    def test_reject_missing_or_duplicate(self):
        for rows in [[], VALID["sections"] * 2]:
            self.assertFalse(self.valid({"sections": rows}))

    def test_reject_free_claims(self):
        d = copy.deepcopy(VALID)
        d["sections"][0]["explanation"] = "로그 분석 완료"
        self.assertFalse(self.valid(d))

    def test_reject_nan_and_boolean(self):
        for value in [math.nan, True]:
            d = copy.deepcopy(VALID)
            d["sections"][0]["cpu_percent"] = value
            self.assertFalse(self.valid(d))

    def test_malformed_draft(self):
        for text in ["plain text", '{"sections":null}', '{"sections":[null]}']:
            self.assertFalse(validate_draft(text, COL)[0])

    def test_condition_and_source_preserved(self):
        text = render_report(COL, ["payments-service"], choices=VALID["sections"])
        self.assertIn("CPU 89.1%", text)
        self.assertIn(runbook_steps(BODY)[3], text)
        self.assertIn("90%를 넘고 지속되면", text)
        self.assertIn("조치 미실행", text)

    def test_healthy_has_no_book(self):
        healthy = {**MON, "status": "healthy", "alerts": [], "cpu_percent": 35.0}
        text = render_report(
            [{"source": "monitoring", "data": healthy}], ["payments-service"]
        )
        self.assertIn("장애 매뉴얼을 적용하지 않았습니다", text)
        self.assertNotIn("DB Down", text)

    def test_insufficient_and_invalid_metrics(self):
        self.assertEqual(monitoring_state({**MON, "alerts": []}), "insufficient")
        self.assertEqual(
            monitoring_state({**MON, "cpu_percent": float("nan")}), "unknown"
        )

    def test_unknown_placeholder_is_not_an_observed_zero(self):
        d = {**MON, "status": "unknown", "cpu_percent": 0, "memory_percent": 0}
        report = render_report(
            [{"source": "monitoring", "data": d}], ["payments-service"]
        )
        self.assertIn("확인할 수 없습니다", report)
        self.assertNotIn("CPU 0%", report)


class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_partial_failure_does_not_cancel_success(self):
        class MCP:
            async def call_tool(self, name, args):
                if args["system_name"] == "auth-service":
                    raise RuntimeError("offline")
                return MON

        result = await collect_monitoring(
            ["payments-service", "auth-service"], MCP(), 1
        )
        self.assertEqual([r["source"] for r in result], ["monitoring", "error"])

    async def test_mismatched_monitoring_target_rejected(self):
        class MCP:
            async def call_tool(self, name, args):
                return MON

        result = await collect_monitoring(["auth-service"], MCP(), 1)
        self.assertEqual(result[0]["source"], "error")

    async def test_lookup_deadline(self):
        class MCP:
            async def call_tool(self, *args):
                await asyncio.sleep(1)

        result = await collect_monitoring(["payments-service"], MCP(), 0.01)
        self.assertEqual(result[0]["source"], "error")

    async def test_healthy_skips_search(self):
        class Search:
            async def search(self, *args):
                raise AssertionError("unexpected search")

        got = await collect_runbooks(
            [
                {
                    "source": "monitoring",
                    "data": {**MON, "status": "healthy", "alerts": []},
                }
            ],
            Search(),
            None,
            1,
        )
        self.assertEqual(got, [])

    async def test_search_failure_is_recorded(self):
        class Search:
            async def search(self, *args):
                return {"matches": []}

        got = await collect_runbooks(COL[:1], Search(), None, 1)
        self.assertEqual(got[-1]["source"], "error")

    async def test_failed_validation_never_forces_pass(self):
        class Fast:
            def plan(self, *args):
                return {"tasks": []}, {"usd": 0}

        class Bad:
            async def write(self, *args):
                return "invalid", {"usd": 0}

        class MCP:
            async def find_prompt(self, *args):
                return "ops"

            async def get_prompt(self, *args, **kw):
                return ""

            async def call_tool(self, name, args):
                return MON

            async def find_resource_template(self, *args):
                return "ops", "runbook://incident-response/{incident_type}"

            async def read_resource(self, *args):
                return BODY

        class Search:
            async def search(self, *args):
                return {
                    "model": "test",
                    "matches": [{"id": "cpu-spike", "score": 1, "title": "CPU"}],
                }

        deps = SupervisorDeps(Fast(), Bad(), MCP(), None, "v2", searcher=Search())
        r = await build_graph(deps).ainvoke(
            {"query": "payments-service CPU가 높아요", "events": []}
        )
        self.assertEqual(r["answer_status"], "fallback")
        self.assertEqual(r["validation_attempts"], 2)
        self.assertIn("완료하지 못해", r["final"])
        self.assertFalse(
            any(e.get("verdict", "").startswith("합격") for e in r["events"])
        )


class RetrievalTests(unittest.TestCase):
    def test_caching_ranking_and_reindex(self):
        class Embed:
            model = "unit-test-only"
            calls = 0

            def embed(self, texts):
                self.calls += 1
                return [
                    normalize([1, 0]) if "CPU" in t else normalize([0, 1])
                    for t in texts
                ]

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            docs = p / "docs"
            docs.mkdir()
            (docs / "cpu.md").write_text("# CPU\n1. CPU 확인")
            (docs / "memory.md").write_text("# Memory\n1. 확인")
            embed = Embed()
            r = RunbookRetriever(docs, p / "index.sqlite", embed)
            self.assertFalse(r.build()["cached"])
            self.assertTrue(r.build()["cached"])
            result = r.search("CPU", k=1)
            self.assertEqual(result["matches"][0]["id"], "cpu")
            (docs / "cpu.md").write_text("# CPU\n1. 문서 변경")
            self.assertFalse(r.build()["cached"])

    def test_empty_corpus_and_zero_vector(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            with self.assertRaises(ValueError):
                RunbookRetriever(p, p / "x.sqlite").build()
        with self.assertRaises(ValueError):
            normalize([0, 0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
