#!/usr/bin/env bash
# Existing processes and session databases are preserved.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN=python3
[[ -x .venv/bin/python3 ]] && PYTHON_BIN=.venv/bin/python3
PORT="${BACKEND_PORT:-8100}"
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "포트 $PORT 사용 중입니다. 기존 서버를 유지합니다. BACKEND_PORT로 다른 포트를 지정해주세요." >&2
  exit 1
fi
if ! curl --fail --silent --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Ollama가 응답하지 않습니다. Ollama 앱 또는 ollama serve를 먼저 실행해주세요." >&2
  exit 1
fi
exec env LLM_BACKEND=ollama "$PYTHON_BIN" -m uvicorn server:app --host 127.0.0.1 --port "$PORT"
