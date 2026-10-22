"""Only for a paired UI demonstration: original MCP logic with jitter fixed to zero."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / "baseline/original_v2/mcp_server.py"
spec = importlib.util.spec_from_file_location("original_ops", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.random.uniform = lambda *_: 0.0
module.mcp.run(show_banner=False)
