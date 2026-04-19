#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-$HOME/.openclaw}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "python or python3 not found in PATH"
  exit 1
fi

for path in \
  "$TARGET_ROOT/skills/workking/SKILL.md" \
  "$TARGET_ROOT/skills/workking/scripts/workking_runner.py" \
  "$TARGET_ROOT/skills/workking/scripts/workking_store.py"
do
  if [ ! -f "$path" ]; then
    echo "missing required file: $path"
    exit 1
  fi
done

"$PYTHON_BIN" "$TARGET_ROOT/skills/workking/scripts/workking_store.py" status
