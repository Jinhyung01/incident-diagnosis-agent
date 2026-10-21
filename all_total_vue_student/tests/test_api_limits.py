import asyncio
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from agent.deps import SupervisorDeps
from fastapi.testclient import TestClient


class MemoryStore:
    def __init__(self):
        self.messages = []

    def load(self, thread):
        return list(self.messages)

    def append(self, thread, role, content):
        self.messages.append({"role": role, "content": content})


class LimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_deadline_preserves_collected_facts(self):
        class Slow:
            async def astream(self, *args, **kwargs):
                yield (
                    "updates",
                    {
                        "monitoring": {
                            "route": "incident",
                            "targets": ["payments-service"],
                            "unknown": [],
                            "collected": [
                                {
                                    "source": "monitoring",
                                    "data": {
                                        "system_name": "payments-service",
                                        "status": "degraded",
                                        "cpu_percent": 89.1,
                                        "memory_percent": 54.1,
                                        "alerts": ["CPU 91%"],
                                        "last_checked": "test",
                                    },
                                }
                            ],
                            "events": [],
                        }
                    },
                )
                await asyncio.sleep(1)

        old_graph = getattr(server.app.state, "graph", None)
        old_deps = getattr(server.app.state, "deps", None)
        server.app.state.graph = Slow()
        server.app.state.backend = "test"
        server.app.state.deps = SupervisorDeps(
            None, None, None, MemoryStore(), "v2", request_timeout=0.02
        )
        try:
            started = time.perf_counter()
            events = [e async for e in server.execute("payments-service", "test")]
            final = events[-1]
            self.assertLess(time.perf_counter() - started, 0.4)
            self.assertEqual(final["metadata"]["answer_status"], "timeout")
            self.assertIn("CPU 89.1%", final["reply"])
            self.assertIn("처리 시간 제한", final["reply"])
            self.assertEqual(
                final["evidence"]["services"][0]["system_name"], "payments-service"
            )
        finally:
            server.app.state.graph = old_graph
            server.app.state.deps = old_deps


class InputTests(unittest.TestCase):
    def test_get_and_post_reject_empty_and_oversized_input(self):
        client = TestClient(server.app)
        for value in ["", "x" * 4001]:
            self.assertEqual(
                client.get("/chat/stream", params={"message": value}).status_code, 422
            )
            self.assertEqual(
                client.post("/chat", json={"message": value}).status_code, 422
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
