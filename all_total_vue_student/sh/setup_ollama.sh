#!/usr/bin/env bash
# Download only missing models. Never stop Ollama or delete an existing model.
set -euo pipefail
command -v ollama >/dev/null || { echo 'Ollama를 먼저 설치해주세요: https://ollama.com'; exit 1; }
curl --fail --silent --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null || { echo 'Ollama 앱 또는 ollama serve를 먼저 실행해주세요.'; exit 1; }
for model in qwen3:0.6b qwen3:8b bge-m3; do
  if ! ollama show "$model" >/dev/null 2>&1; then ollama pull "$model"; fi
done
