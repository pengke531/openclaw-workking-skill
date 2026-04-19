#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-$HOME/.openclaw}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILL_SOURCE="$REPO_ROOT/skill/workking"
SKILL_TARGET="$TARGET_ROOT/skills/workking"
CONFIG_SOURCE="$SKILL_SOURCE/references/workking.config.example.json"
CONFIG_ROOT="$TARGET_ROOT/data/workking"
CONFIG_TARGET="$CONFIG_ROOT/workking.config.json"

if [ ! -d "$SKILL_SOURCE" ]; then
  echo "missing skill source: $SKILL_SOURCE"
  exit 1
fi

mkdir -p "$(dirname "$SKILL_TARGET")"
rm -rf "$SKILL_TARGET"
cp -R "$SKILL_SOURCE" "$SKILL_TARGET"
mkdir -p "$CONFIG_ROOT"
if [ -f "$CONFIG_SOURCE" ] && [ ! -f "$CONFIG_TARGET" ]; then
  cp "$CONFIG_SOURCE" "$CONFIG_TARGET"
fi

echo "[workking] installed to: $SKILL_TARGET"
echo "[workking] config path:  $CONFIG_TARGET"
echo "[workking] next: start a new OpenClaw session, then run /workking"
