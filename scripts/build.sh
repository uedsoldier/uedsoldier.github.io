#!/bin/sh
# Build wrapper: use project's venv python if available, else fallback to system python

set -e

PY=""
if [ -x "./venv/bin/python" ]; then
  PY="./venv/bin/python"
elif [ -x "./.venv/bin/python" ]; then
  PY="./.venv/bin/python"
elif [ -x "./env/bin/python" ]; then
  PY="./env/bin/python"
elif command -v python >/dev/null 2>&1; then
  PY="python"
fi

if [ -z "$PY" ]; then
  echo "No Python interpreter found (checked ./venv, ./.venv, ./env, system python)"
  exit 1
fi

if [ ! -f "scripts/build.py" ]; then
  echo "scripts/build.py not found; nothing to build."
  exit 1
fi

echo "Using Python: $PY"
exec "$PY" "scripts/build.py" "$@"
