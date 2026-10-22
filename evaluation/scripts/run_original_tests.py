"""Exercise all ten documented regression queries over actual HTTP SSE/MCP.

Uses only local Ollama, preserved original source, a separate SQLite DB and
separate backend/proxy processes. Original application files are never edited.
"""
import argparse
import hashlib
import html
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "baseline/original_v2"
QUERIES = [
    ("Q01", "payments-service 결제 응답이 느려지고 CPU가 치솟았어요, 원인 확인해주세요", "payments 인식 및 cpu-spike 매뉴얼 선택"),
    ("Q02", "cache-service 메모리 사용률이 계속 올라가고 있어요", "cache 인식 및 memory-leak 매뉴얼 선택"),
    ("Q03", "log-service 디스크 공간이 부족하다는 알림이 왔어요", "log-service 인식 및 disk-full 매뉴얼 선택"),
    ("Q04", "gateway-service에서 payments-service로 가는 요청이 타임아웃 나고 있어요", "대표 라벨 gateway와 별개로 두 서비스 조사"),
    ("Q05", "web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘", "web-01과 auth-service 동시 조사 회귀 확인"),
    ("Q06", "payments-service랑 cache-service 둘 다 저하됐는데 공통 원인이 있는지 분석해줘", "needs_analysis·gate·분석 실행 및 비교 대상 수집 확인"),
    ("Q07", "로그인 응답이 느려요, 원인 확인해주세요", "원래 정책: 대상 미명시 시 auth-service 기본 처리"),
    ("Q08", "billing-service 응답이 느려요", "원래 정책: 미등록 대상 보정 및 auth-service 기본 처리"),
    ("Q09", "안녕, 너는 누구야?", "chat 직접 분기 및 FinalAnswer 전 AnswerToken 전달"),
    ("Q10", "제 이름은 민수입니다 → 서버 재시작 → 제 이름이 뭐였죠?", "같은 thread의 SQLite 재시작 유지 및 SSE 응답 확인"),
]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_observations(out):
    p = out / "observations.ndjson"
    return [json.loads(s) for s in p.read_text().splitlines()] if p.exists() else []


def summarize(out, case):
    obs = [r for r in read_observations(out) if r.get("thread_id") == case["thread_id"]]
    tools = [r["data"] for r in obs if r["kind"] == "tool_result"]
    books = list(dict.fromkeys(r["uri"].rsplit("/", 1)[-1] for r in obs if r["kind"] == "mcp_resource"))
    targets = sorted({r["system_name"] for r in tools})
    stages = [r for r in obs if r["kind"] in {"llm_start", "llm_end", "llm_error"}]
    case.update(observations=obs, targets=targets, runbooks=books, monitoring=tools,
                stages=stages, elapsed_seconds=round(sum(t["elapsed_seconds"] for t in case["turns"]), 3))
    expected = {
        "Q01": (["payments-service"], "cpu-spike"),
        "Q02": (["cache-service"], "memory-leak"),
        "Q03": (["log-service"], "disk-full"),
        "Q04": (["gateway-service", "payments-service"], None),
        "Q05": (["auth-service", "web-01"], None),
        "Q06": (["cache-service", "payments-service"], None),
        "Q07": (["auth-service"], None), "Q08": (["auth-service"], None),
    }
    checks = {}
    if case["id"] in expected:
        exp, book = expected[case["id"]]
        checks["original_target_selection"] = targets == sorted(exp)
        if book:
            checks["original_runbook_selection"] = book in books
    if case["id"] == "Q04":
        checks["prompt_label_is_gateway"] = any(r["kind"] == "mcp_prompt" and r["arguments"].get("system_name") == "gateway-service" for r in obs)
    if case["id"] == "Q08":
        checks["prompt_label_is_auth"] = any(r["kind"] == "mcp_prompt" and r["arguments"].get("system_name") == "auth-service" for r in obs)
        plans = [r["output"] for r in obs if r["kind"] == "llm_end" and r["stage"] == "fast.plan"]
        monitoring_tasks = [t for p in plans[-1:] for t in p["tasks"] if t.get("kind") == "monitoring"]
        checks["plan_target_clamped_to_auth"] = bool(monitoring_tasks) and all(t.get("target") == "auth-service" for t in monitoring_tasks)
    if case["id"] == "Q06":
        plans = [r for r in obs if r["kind"] == "llm_end" and r["stage"] == "fast.plan"]
        checks["plan_needs_analysis"] = bool(plans and plans[-1]["output"].get("needs_analysis"))
        events = [e["data"] for t in case["turns"] for e in t["events"]]
        checks["analysis_task_retained"] = any(r.get("agent") == "analysis" for p in plans for r in p["output"].get("tasks", [])) and any(e.get("type") == "GateApplied" and e.get("removed_analysis_tasks") == 0 for e in events)
        checks["analysis_completed"] = any(r["kind"] == "llm_end" and r["stage"] == "fast.analyze" for r in obs)
    if case["id"] == "Q09":
        events = [e["data"] for t in case["turns"] for e in t["events"]]
        checks["chat_route"] = any(e.get("type") == "RouteDecided" and e.get("route") == "chat" for e in events)
        checks["no_monitoring_or_runbook"] = not tools and not books
        checks["answer_tokens_before_final"] = all(t["stream_checks"]["tokens_before_final"] for t in case["turns"])
    if case["id"] == "Q10":
        checks.update(case.get("restart_checks", {}))
        last = case["turns"][-1]
        checks["history_in_final_prompt"] = "user: 제 이름은 민수입니다" in (last.get("prompt") or "")
        checks["answer_contains_name"] = "민수" in last.get("reply", "")
        checks["answer_tokens_before_final"] = last["stream_checks"]["tokens_before_final"]
        case["name_role_review"] = "AI-assisted review pending; name presence alone does not prove correct user/assistant attribution."
    if case["id"] in {"Q09", "Q10"}:
        checks["token_concat_matches_final"] = all(t["stream_checks"]["joined_tokens_match_final"] for t in case["turns"])
    case["original_purpose_checks"] = checks
    case["response_complete"] = all(t["done"] and t["final_received"] and not t["error"] for t in case["turns"])
    case["status"] = "completed" if case["response_complete"] else "incomplete"
    save(out / f"{case['id']}.json", case)


def request(client, out, case, message, suffix):
    started = time.monotonic()
    record = {"message": message, "events": [], "reply": "", "prompt": None,
              "done": False, "final_received": False, "error": None}
    path = out / f"{case['id']}-{suffix}.sse.ndjson"
    print(f"START {case['id']} {suffix}: {message}", flush=True)
    try:
        with path.open("w") as f, client.stream("GET", "http://127.0.0.1:8701/chat/stream",
                params={"message": message, "thread_id": case["thread_id"]}) as response:
            response.raise_for_status()
            record["http_status"] = response.status_code
            record["content_type"] = response.headers.get("content-type")
            for line in response.iter_lines():
                if not line.startswith("data:"):
                    continue
                value = line[5:].strip()
                elapsed = round(time.monotonic() - started, 6)
                data = {"type": "DONE"} if value == "[DONE]" else json.loads(value)
                event = {"elapsed_seconds": elapsed, "data": data}
                record["events"].append(event)
                f.write(json.dumps(event, ensure_ascii=False) + "\n"); f.flush()
                if data.get("type") == "FinalAnswer":
                    record.update(reply=data.get("reply", ""), prompt=data.get("prompt"), final_received=True)
                elif data.get("type") == "DONE":
                    record["done"] = True
                if data.get("type") not in {"AnswerToken"}:
                    print(f"EVENT {case['id']} {elapsed:.2f}s {data.get('type')}", flush=True)
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    tokens = [(i, e) for i, e in enumerate(record["events"]) if e["data"].get("type") == "AnswerToken"]
    finals = [(i, e) for i, e in enumerate(record["events"]) if e["data"].get("type") == "FinalAnswer"]
    record["stream_checks"] = {
        "token_events": len(tokens),
        "first_token_seconds": tokens[0][1]["elapsed_seconds"] if tokens else None,
        "final_seconds": finals[-1][1]["elapsed_seconds"] if finals else None,
        "tokens_before_final": bool(tokens and finals and tokens[0][0] < finals[-1][0] and tokens[0][1]["elapsed_seconds"] < finals[-1][1]["elapsed_seconds"]),
        "joined_tokens_match_final": bool(finals) and "".join(e["data"].get("delta", "") for _, e in tokens) == record["reply"],
    }
    case["turns"].append(record)
    summarize(out, case)
    print(f"DONE {case['id']} {suffix}: {record['elapsed_seconds']}s complete={record['done']} error={record['error']}", flush=True)


def rows(db, thread):
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as c:
        return c.execute("SELECT role,content FROM messages WHERE thread_id=? ORDER BY rowid", (thread,)).fetchall()


def run(args):
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    for port in [8201, 8701]:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is in use; no existing process was stopped")
    out.mkdir(parents=True)
    config = {"created_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "client_date": "2026-10-21", "source": str(SOURCE), "models": ["qwen3:0.6b", "qwen3:8b"],
        "mode": "original HTTP SSE + original proxy + actual MCP subprocesses + local Ollama",
        "monitoring": "original random jitter; not fixed-data before/after comparison",
        "changes": ["isolated SQLite path", "backend/proxy ports", "observational method wrappers"],
        "source_files": {str(p.relative_to(SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob('*') if p.is_file()},
        "query_purposes": [{"id": i, "query": q, "purpose": p} for i,q,p in QUERIES],
        "original_launch_scripts_executed": False,
        "launch_script_deletes_session_db": "rm -f session.db" in (SOURCE / "sh/run_agent_ollma.sh").read_text()}
    save(out / "config.json", config)
    env = {**os.environ, "LANGCHAIN_TRACING_V2":"false", "LANGSMITH_TRACING":"false",
           "LLM_BACKEND":"ollama", "SUPERVISOR_VERSION":"v2", "PYTHONDONTWRITEBYTECODE":"1"}
    handles, processes = [], []

    def start(mode, port):
        log = (out / f"{mode}.log").open("a"); handles.append(log)
        proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name('serve_original.py')),
            "--mode", mode, "--source", str(SOURCE), "--output", str(out), "--port", str(port)],
            cwd=out, env=env, stdout=log, stderr=log, start_new_session=True)
        processes.append(proc)
        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError(f"{mode} exited; inspect local {mode}.log")
            try:
                r=httpx.get(f"http://127.0.0.1:{port}/health", timeout=2)
                if r.status_code==200: return proc,r.json()
            except httpx.HTTPError: pass
            time.sleep(0.25)
        raise TimeoutError(f"{mode} startup")

    def stop(proc):
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try: proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)

    cases=[]
    try:
        backend,health=start("backend",8201)
        proxy,_=start("proxy",8701)
        config["backend_health"]=health;save(out/"config.json",config)
        with httpx.Client(timeout=httpx.Timeout(connect=10,read=360,write=20,pool=10),trust_env=False) as client:
            for id,query,purpose in QUERIES:
                case={"id":id,"query":query,"purpose":purpose,"thread_id":f"verify-{id}","turns":[]}
                if id!="Q10":request(client,out,case,query,"turn1")
                else:
                    request(client,out,case,"제 이름은 민수입니다","before-restart")
                    before=rows(out/"session.db",case['thread_id']);old_pid=backend.pid
                    stop(backend);backend,_=start("backend",8201)
                    after=rows(out/"session.db",case['thread_id'])
                    case['restart_checks']={"process_pid_changed":backend.pid!=old_pid,
                        "sqlite_rows_preserved":bool(before) and before==after,
                        "user_name_persisted":any(role=='user' and '민수' in content for role,content in after)}
                    case['restart_evidence']={"before_pid":old_pid,"after_pid":backend.pid,"before_rows":before,"after_rows":after}
                    request(client,out,case,"제 이름이 뭐였죠?","after-restart")
                cases.append(case);save(out/"results.json",cases)
    finally:
        for proc in reversed(processes):stop(proc)
        for f in handles:f.close()
    for name,digest in config['source_files'].items():
        assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==digest,name
    save(out/'completion.json',{'cases':len(cases),'source_unchanged':True,'test_processes_stopped':True})
    print(f"FINISHED {len(cases)} cases: {out}",flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args())
