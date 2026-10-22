"""Actual MCP + HTTP proxy + SSE + SQLite restart verification on isolated ports."""

import argparse
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "all_total_vue_student"
CASES = [
    (
        "Q01",
        "payments-service 결제 응답이 느려지고 CPU가 치솟았어요, 원인 확인해주세요",
        ["payments-service"],
        ["cpu-spike"],
    ),
    (
        "Q02",
        "cache-service 메모리 사용률이 계속 올라가고 있어요",
        ["cache-service"],
        ["memory-leak"],
    ),
    (
        "Q03",
        "log-service 디스크 공간이 부족하다는 알림이 왔어요",
        ["log-service"],
        ["disk-full"],
    ),
    (
        "Q04",
        "gateway-service에서 payments-service로 가는 요청이 타임아웃 나고 있어요",
        ["gateway-service", "payments-service"],
        ["network-timeout", "cpu-spike"],
    ),
    (
        "Q05",
        "web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘",
        ["web-01", "auth-service"],
        ["high-latency"],
    ),
    (
        "Q06",
        "payments-service랑 cache-service 둘 다 저하됐는데 공통 원인이 있는지 분석해줘",
        ["payments-service", "cache-service"],
        ["cpu-spike", "memory-leak"],
    ),
    ("Q07", "로그인 응답이 느려요, 원인 확인해주세요", [], []),
    ("Q08", "billing-service 응답이 느려요", [], []),
    ("Q09", "안녕, 너는 누구야?", [], []),
]


def main(out):
    out = out.resolve()
    if out.exists():
        raise FileExistsError(out)
    for port in [8204, 8704]:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} already used")
    out.mkdir(parents=True)
    processes = []
    logs = []
    env = {
        **os.environ,
        "LLM_BACKEND": "ollama",
        "PROJECT_TRACING": "false",
        "MONITORING_FIXED": "true",
        "SIMULATE_FIRST_TIMEOUT": "true",
        "PYTHONDONTWRITEBYTECODE": "1",
        "SESSION_DB_PATH": str(out / "session.db"),
        "BACKEND_URL": "http://127.0.0.1:8204",
    }

    def stop(p):
        if p.poll() is None:
            os.killpg(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait(timeout=5)

    def start(mode):
        module, port = (
            ("server", 8204) if mode == "backend" else ("web_demo_server", 8704)
        )
        log = (out / f"{mode}.log").open("a")
        logs.append(log)
        p = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                module + ":app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=SOURCE,
            env=env,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
        processes.append(p)
        for _ in range(100):
            if p.poll() is not None:
                raise RuntimeError(f"{mode} startup failed")
            try:
                r = httpx.get(
                    f"http://127.0.0.1:{port}/health", timeout=1, trust_env=False
                )
                if r.status_code == 200:
                    return p, r.json()
            except httpx.HTTPError:
                pass
            time.sleep(0.2)
        raise TimeoutError("startup")

    records = []

    def save():
        (out / "results.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n"
        )

    def request(id, query, thread, expected, books):
        print("START", id, query, flush=True)
        started = time.perf_counter()
        events = []
        final = None
        with (
            httpx.Client(timeout=75, trust_env=False) as c,
            c.stream(
                "GET",
                "http://127.0.0.1:8704/chat/stream",
                params={"message": query, "thread_id": thread},
            ) as response,
        ):
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                e = {"type": "DONE"} if raw == "[DONE]" else json.loads(raw)
                events.append(
                    {"seconds": round(time.perf_counter() - started, 6), "data": e}
                )
                if e["type"] == "FinalAnswer":
                    final = e
        assert final is not None
        services = final.get("evidence", {}).get("services", [])
        actual = sorted(s["system_name"] for s in services)
        actual_books = sorted({s["runbook"]["id"] for s in services if s["runbook"]})
        tokens = [
            (i, e) for i, e in enumerate(events) if e["data"]["type"] == "AnswerToken"
        ]
        final_idx = next(
            i for i, e in enumerate(events) if e["data"]["type"] == "FinalAnswer"
        )
        checks = {
            "target_scope": actual == sorted(expected),
            "book_scope": actual_books == sorted(books),
            "done": events[-1]["data"]["type"] == "DONE",
            "tokens_before_final": bool(tokens) and tokens[0][0] < final_idx,
            "token_concat_matches_final": "".join(e["data"]["delta"] for _, e in tokens)
            == final["reply"],
        }
        record = {
            "id": id,
            "query": query,
            "thread_id": thread,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "actual_targets": actual,
            "actual_books": actual_books,
            "checks": checks,
            "final": final,
            "events": events,
        }
        records.append(record)
        save()
        print("DONE", id, checks, flush=True)
        return record

    try:
        backend, health = start("backend")
        proxy, _ = start("proxy")
        (out / "config.json").write_text(
            json.dumps(
                {
                    "health": health,
                    "monitoring": "fixed original base values; actual MCP transport",
                    "ports": [8204, 8704],
                    "simulated_first_timeout": True,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        for id, q, targets, books in CASES:
            request(id, q, "integration-" + id, targets, books)
        request("Q10-first", "제 이름은 민수입니다", "integration-name", [], [])
        with sqlite3.connect(out / "session.db") as db:
            before = db.execute(
                "SELECT role,content FROM messages WHERE thread_id=? ORDER BY rowid",
                ("integration-name",),
            ).fetchall()
        old_pid = backend.pid
        stop(backend)
        backend, _ = start("backend")
        with sqlite3.connect(out / "session.db") as db:
            after = db.execute(
                "SELECT role,content FROM messages WHERE thread_id=? ORDER BY rowid",
                ("integration-name",),
            ).fetchall()
        last = request(
            "Q10-after-restart", "제 이름이 뭐였죠?", "integration-name", [], []
        )
        restart = {
            "pid_changed": old_pid != backend.pid,
            "same_rows": before == after,
            "user_name_correct": "사용자님의 이름은 민수입니다."
            == last["final"]["reply"],
            "before_pid": old_pid,
            "after_pid": backend.pid,
        }
        (out / "restart.json").write_text(
            json.dumps(restart, ensure_ascii=False, indent=2)
        )
        assert all(all(r["checks"].values()) for r in records), (
            "Integration checks failed"
        )
        assert all(
            restart[k] for k in ["pid_changed", "same_rows", "user_name_correct"]
        )
        assert records[0]["final"]["metadata"]["retry_count"] == 1
        (out / "SUMMARY.md").write_text(
            "# 실제 MCP·HTTP·SSE 통합 검증\n\n원본 문서의 10개 입력 목적을 개선 정책에 맞춰 검증했다. 실제 로컬 모델·임베딩·MCP subprocess·원본 프록시를 통과했다. 고정 모의 지표를 사용했다.\n\n- 10개 시나리오, 이름 입력/재질문을 포함한 11개 요청의 대상·매뉴얼·SSE 종료·최종 내용 일치 확인\n- 최초 모니터링 호출의 의도적 시간 초과를 1회 재시도해 복구\n- 별도 SQLite DB와 같은 thread를 유지한 서버 재시작 후 사용자 이름을 올바르게 응답\n- 일반 대화는 즉시 답하고 장애 답변은 검증 후 조각을 전송한다. 검증 전 LLM 초안을 실시간 공개하지 않는다.\n- 웹 UI 화면 자체는 docs/evidence/after의 별도 실제 브라우저 캡처로 확인한다.\n"
        )
    finally:
        for p in reversed(processes):
            stop(p)
        for log in logs:
            log.close()
    print("Integration verification complete", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    main(parser.parse_args().output)
