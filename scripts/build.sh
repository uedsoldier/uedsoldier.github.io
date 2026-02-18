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
# Merge standalone JSON bundles into data/portfolio.json before building.
# This keeps `data/portfolio.json` in sync with per-section files used for editing.
echo "Merging data bundles into data/portfolio.json..."
# Ensure per-project files are assembled into data/projects.json first
echo "Assembling per-project files into data/projects.json..."
"$PY" "scripts/assemble_projects_bundle.py" --projects-dir data/projects --out data/projects.json || {
  echo "Warning: assemble_projects_bundle.py failed (continuing to merge)" >&2
}

# If portfolio.json is missing, abort — user must provide or restore it.
if [ ! -f data/portfolio.json ]; then
  echo "Error: data/portfolio.json not found. Please restore or generate it before building." >&2
  exit 1
fi

"$PY" "scripts/merge_into_portfolio.py" --input data/portfolio.json --files data/education.json --files data/contact.json --files data/skills.json --files data/projects.json || {
  echo "Warning: merge script failed (continuing to build)" >&2
}

exec "$PY" "scripts/build.py" "$@"
