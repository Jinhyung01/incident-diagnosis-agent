"""Launch preserved source with isolated ports/SQLite and observational logging.

Only the SQLite path and service ports change. Original graph, models, MCP
transport, random monitoring data and generation settings remain unchanged.
"""
import argparse
import contextvars
import functools
import inspect
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

CASE = contextvars.ContextVar("verification_case", default={})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["backend", "proxy"], required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--backend-port", type=int, default=8201)
    args = p.parse_args()
    os.environ.update(LANGCHAIN_TRACING_V2="false", LANGSMITH_TRACING="false",
                      LLM_BACKEND="ollama", SUPERVISOR_VERSION="v2",
                      PYTHONDONTWRITEBYTECODE="1")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.source.resolve()))
    import uvicorn

    if args.mode == "proxy":
        import web_demo_server
        web_demo_server.BACKEND = f"http://127.0.0.1:{args.backend_port}"
        uvicorn.run(web_demo_server.app, host="127.0.0.1", port=args.port,
                    log_level="warning")
        return

    import server

    def record(kind, **data):
        item = {"kind": kind, "time": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
                "monotonic": time.monotonic(), "pid": os.getpid(),
                **CASE.get(), **data}
        with (args.output / "observations.ndjson").open("a") as f:
            f.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")

    original_store = server.SqliteSessionStore
    server.SqliteSessionStore = lambda: original_store(args.output / "session.db")
    original_factory = server._build_llms

    def observed_method(fn, label):
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def wrapped(*a, **kw):
                record("llm_start", stage=label)
                try:
                    result = await fn(*a, **kw)
                except Exception as exc:
                    record("llm_error", stage=label, error=type(exc).__name__, message=str(exc))
                    raise
                record("llm_end", stage=label, output=result[0],
                       usage={k: v for k, v in result[1].items() if k != "prompt"})
                return result
        else:
            @functools.wraps(fn)
            def wrapped(*a, **kw):
                record("llm_start", stage=label)
                try:
                    result = fn(*a, **kw)
                except Exception as exc:
                    record("llm_error", stage=label, error=type(exc).__name__, message=str(exc))
                    raise
                record("llm_end", stage=label, output=result[0],
                       usage={k: v for k, v in result[1].items() if k != "prompt"})
                return result
        return wrapped

    def factory():
        backend, fast, quality = original_factory()
        for model, role, names in [(fast, "fast", ["route", "plan", "analyze", "chat"]),
                                   (quality, "quality", ["write"])]:
            for name in names:
                setattr(model, name, observed_method(getattr(model, name), f"{role}.{name}"))
        return backend, fast, quality

    server._build_llms = factory
    original_mcp = server.MCPClient

    class ObservedMCP(original_mcp):
        async def call_tool(self, name, arguments, server="ops"):
            record("tool_start", name=name, arguments=arguments, mcp_server=server)
            try:
                result = await super().call_tool(name, arguments, server=server)
            except Exception as exc:
                record("tool_error", name=name, error=type(exc).__name__, message=str(exc))
                raise
            record("tool_result", name=name, data=result, mcp_server=server)
            return result

        async def get_prompt(self, name, arguments, server="ops"):
            result = await super().get_prompt(name, arguments, server=server)
            record("mcp_prompt", name=name, arguments=arguments, body=result, mcp_server=server)
            return result

        async def read_resource(self, uri, server):
            result = await super().read_resource(uri, server)
            record("mcp_resource", uri=uri, body=result, mcp_server=server)
            return result

    server.MCPClient = ObservedMCP

    class ContextApp:
        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                return await server.app(scope, receive, send)
            from urllib.parse import parse_qs
            qs = parse_qs(scope.get("query_string", b"").decode())
            token = CASE.set({"thread_id": qs.get("thread_id", [""])[0],
                              "query": qs.get("message", [""])[0]})
            try:
                await server.app(scope, receive, send)
            finally:
                CASE.reset(token)

    record("server_start", database="session.db", source=str(args.source))
    uvicorn.run(ContextApp(), host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
