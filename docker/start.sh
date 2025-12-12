#!/usr/bin/env sh
set -eu

BACKEND_PORT="${BACKEND_PORT:-7861}"
export GRADIO_SERVER_PORT="${BACKEND_PORT}"
export GRADIO_SERVER_NAME="${GRADIO_SERVER_NAME:-0.0.0.0}"

python -u mb_app.py &
BACKEND_PID="$!"

cleanup() {
  kill "${BACKEND_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

exec nginx -g "daemon off;"

