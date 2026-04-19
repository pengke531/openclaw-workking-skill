#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-$HOME/.openclaw}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILL_SOURCE="$REPO_ROOT/skill/workking"
SKILL_TARGET="$TARGET_ROOT/skills/workking"

if [ ! -d "$SKILL_SOURCE" ]; then
  echo "missing skill source: $SKILL_SOURCE"
  exit 1
fi

mkdir -p "$(dirname "$SKILL_TARGET")"
rm -rf "$SKILL_TARGET"
cp -R "$SKILL_SOURCE" "$SKILL_TARGET"

echo "[workking] installed to: $SKILL_TARGET"
echo "[workking] next: start a new OpenClaw session, then run /workking"
