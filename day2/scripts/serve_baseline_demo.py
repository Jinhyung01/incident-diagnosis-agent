"""Launch the preserved original backend/proxy for paired actual UI screenshots."""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "day1/baseline/original_v2"
parser = argparse.ArgumentParser()
parser.add_argument("--proxy", action="store_true")
args = parser.parse_args()
os.environ.update(
    LLM_BACKEND="ollama",
    SUPERVISOR_VERSION="v2",
    LANGCHAIN_TRACING_V2="false",
    LANGSMITH_TRACING="false",
    PYTHONDONTWRITEBYTECODE="1",
)
sys.path.insert(0, str(SOURCE))
import uvicorn

if args.proxy:
    import web_demo_server

    web_demo_server.BACKEND = "http://127.0.0.1:8203"
    uvicorn.run(web_demo_server.app, host="127.0.0.1", port=8703, log_level="warning")
else:
    import server
    from agent.mcp_client import MCPClient
    from agent.session_store import SqliteSessionStore

    out = ROOT / "day2/runtime/baseline-ui"
    out.mkdir(parents=True, exist_ok=True)
    server.MCPClient = lambda: MCPClient(
        flaky_first_tool_call=False,
        server_scripts={
            "ops": ROOT / "day2/scripts/fixed_original_mcp.py",
            "docs": SOURCE / "mcp_server_docs.py",
        },
    )
    server.SqliteSessionStore = lambda: SqliteSessionStore(out / "session.db")
    uvicorn.run(server.app, host="127.0.0.1", port=8203, log_level="warning")
