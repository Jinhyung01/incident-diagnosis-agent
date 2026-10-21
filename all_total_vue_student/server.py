"""FastAPI application with a bounded request lifetime and explicit evidence output."""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
if os.environ.get("PROJECT_TRACING") != "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGSMITH_TRACING"] = "false"

from agent.deps import SupervisorDeps
from agent.evidence import evidence_payload, render_report
from agent.graph import build_graph
from agent.mcp_client import MCPClient
from agent.retrieval import MCPRunbookSearch
from agent.session_store import SqliteSessionStore
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


def _build_llms():
    backend = os.environ.get("LLM_BACKEND", "ollama")
    from agent.ollama_llm import OllamaFastLLM

    if backend == "ollama":
        from agent.reporting import StructuredReportLLM

        return (
            backend,
            OllamaFastLLM(os.environ.get("OLLAMA_FAST_MODEL", "qwen3:0.6b"), 0.00015),
            StructuredReportLLM(
                os.environ.get("OLLAMA_QUALITY_MODEL", "qwen3:8b"), 0.005
            ),
        )
    if backend == "fake":
        from agent.fake_llm import FastLLM
        from agent.reporting import DeterministicReportStub

        return backend, FastLLM("offline-test-stub", 0), DeterministicReportStub()
    raise ValueError(
        "개선 버전은 ollama 또는 fake를 지원합니다. OpenAI 경로는 원본에 보존했습니다."
    )


@asynccontextmanager
async def lifespan(app):
    mcp = MCPClient(
        flaky_first_tool_call=os.environ.get("SIMULATE_FIRST_TIMEOUT", "false")
        == "true"
    )
    await mcp.start()
    backend, fast, quality = _build_llms()
    db = Path(
        os.environ.get("SESSION_DB_PATH", str(Path(__file__).parent / "session.db"))
    )
    db.parent.mkdir(parents=True, exist_ok=True)
    deps = SupervisorDeps(
        fast,
        quality,
        mcp,
        SqliteSessionStore(db),
        "v2",
        searcher=MCPRunbookSearch(mcp),
        request_timeout=float(os.environ.get("REQUEST_TIMEOUT_SECONDS", "60")),
        call_timeout=float(os.environ.get("LLM_CALL_TIMEOUT_SECONDS", "25")),
    )
    app.state.deps = deps
    app.state.graph = build_graph(deps)
    app.state.backend = backend
    try:
        yield
    finally:
        await mcp.stop()
        deps.session_store.close()


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(default="default", min_length=1, max_length=100)


@app.get("/health")
async def health():
    deps = app.state.deps
    return {
        "status": "ok",
        "implementation": "improved-v2",
        "supervisor_version": "v2",
        "llm_backend": app.state.backend,
        "fast_llm": deps.fast_llm.name,
        "quality_llm": deps.quality_llm.name,
        "request_timeout_seconds": deps.request_timeout,
        "max_writes": deps.max_writes,
        "embedding_model": os.environ.get("EMBEDDING_MODEL", "bge-m3"),
    }


@app.get("/version")
async def version():
    return {"supervisor_version": "v2", "implementation": "improved-v2"}


async def execute(message, thread_id):
    deps = app.state.deps
    started = time.perf_counter()
    state = {
        "query": message,
        "thread_id": thread_id,
        "history": deps.session_store.load(thread_id),
        "events": [],
        "cost_usd": 0.0,
        "collected": [],
        "targets": [],
        "unknown": [],
    }
    seen = 0
    try:
        async with asyncio.timeout(deps.request_timeout):
            async for mode, payload in app.state.graph.astream(
                state, stream_mode=["updates", "custom"]
            ):
                if mode == "custom":
                    yield payload
                    continue
                for node, delta in payload.items():
                    state.update(delta)
                    if "events" in delta:
                        for event in delta["events"][seen:]:
                            yield {**event, "node": node}
                        seen = len(delta["events"])
    except Exception as exc:  # noqa: BLE001 - HTTP boundary must preserve partial facts.
        reason = "처리 시간 제한" if isinstance(exc, TimeoutError) else "요청 처리 실패"
        state["answer_status"] = (
            "timeout" if isinstance(exc, TimeoutError) else "fallback"
        )
        notice = (
            "처리 시간 제한에 도달해 조사를 완료하지 못했습니다."
            if isinstance(exc, TimeoutError)
            else "요청 처리에 실패해 조사를 완료하지 못했습니다."
        )
        state["final"] = render_report(
            state.get("collected", []),
            state.get("targets", []),
            state.get("unknown", []),
            notice=f"{notice} 현재까지 확인한 내용만 안내합니다.",
        )
        state["evidence"] = evidence_payload(
            state.get("collected", []),
            state.get("targets", []),
            state.get("unknown", []),
        )
        yield {
            "type": "RequestLimited",
            "reason": reason,
            "error_type": type(exc).__name__,
        }
    final = (
        state.get("final")
        or "응답을 완료하지 못했습니다. 서비스 이름과 요청을 다시 확인해주세요."
    )
    metadata = {
        "answer_status": state.get("answer_status"),
        "route": state.get("route"),
        "targets": state.get("targets", []),
        "validation_attempts": state.get("validation_attempts", 0),
        "validation_issues": state.get("validation_issues", []),
        "retry_count": state.get("retry_count", 0),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "request_timeout_seconds": deps.request_timeout,
        "delivery": "validated-report-chunks"
        if state.get("route") == "incident"
        else "chat",
        "llm_backend": app.state.backend,
        "implementation": "improved-v2",
    }
    deps.session_store.append(thread_id, "user", message)
    deps.session_store.append(thread_id, "assistant", final)
    yield {
        "type": "FinalAnswer",
        "reply": final,
        "prompt": state.get("last_prompt"),
        "evidence": state.get("evidence", {}),
        "metadata": metadata,
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    all_events = []
    final = {}
    async for event in execute(request.message, request.thread_id):
        if event["type"] == "FinalAnswer":
            final = event
        else:
            all_events.append(event)
    return {**{k: v for k, v in final.items() if k != "type"}, "events": all_events}


@app.get("/chat/stream")
async def stream(
    message: str = Query(min_length=1, max_length=4000),
    thread_id: str = Query(default="default", min_length=1, max_length=100),
):
    # Validate the same limits for GET/SSE and POST.
    request = ChatRequest(message=message, thread_id=thread_id)

    async def generate():
        async for event in execute(request.message, request.thread_id):
            yield "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("BACKEND_PORT", "8100")))
