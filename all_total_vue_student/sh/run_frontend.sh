#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN=python3
[[ -x .venv/bin/python3 ]] && PYTHON_BIN=.venv/bin/python3
PORT="${FRONTEND_PORT:-8600}"
BACKEND="${BACKEND_URL:-http://127.0.0.1:8100}"
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "포트 $PORT 사용 중입니다. 기존 서버를 유지합니다. FRONTEND_PORT로 다른 포트를 지정해주세요." >&2
  exit 1
fi
if ! curl --fail --silent --max-time 2 "$BACKEND/health" >/dev/null; then
  echo "백엔드 $BACKEND 가 응답하지 않습니다. 먼저 백엔드를 실행해주세요." >&2
  exit 1
fi
exec env BACKEND_URL="$BACKEND" "$PYTHON_BIN" -m uvicorn web_demo_server:app --host 127.0.0.1 --port "$PORT"
