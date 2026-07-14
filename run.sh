#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

PORT="${PORT:-8080}"

echo "==> Subindo API em http://localhost:${PORT} (Ctrl+C para parar)"
exec python3 -m gunicorn -b 0.0.0.0:${PORT} main:app