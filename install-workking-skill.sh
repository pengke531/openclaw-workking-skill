#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-$HOME/.openclaw}"
AGENT_ID="${AGENT_ID:-main}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SOURCE_ROOT="$REPO_ROOT/skill"
PATCH_SCRIPT="$REPO_ROOT/scripts/patch_openclaw_exec.py"
CONFIG_SOURCE="$SKILLS_SOURCE_ROOT/workking/references/workking.config.example.json"
CONFIG_ROOT="$TARGET_ROOT/data/workking"
CONFIG_TARGET="$CONFIG_ROOT/workking.config.json"
WITH_CONFIG="${WITH_CONFIG:-0}"

if [ ! -d "$SKILLS_SOURCE_ROOT" ]; then
  echo "missing skills source root: $SKILLS_SOURCE_ROOT"
  exit 1
fi

mkdir -p "$TARGET_ROOT/skills"
FOUND_SKILL=0
for skill_dir in "$SKILLS_SOURCE_ROOT"/workking* "$SKILLS_SOURCE_ROOT"/work[1-7]; do
  if [ -d "$skill_dir" ]; then
    FOUND_SKILL=1
    skill_name="$(basename "$skill_dir")"
    skill_target="$TARGET_ROOT/skills/$skill_name"
    rm -rf "$skill_target"
    cp -R "$skill_dir" "$skill_target"
    echo "[workking] installed skill: $skill_name -> $skill_target"
  fi
done

if [ "$FOUND_SKILL" = "0" ]; then
  echo "no workking skill directories found under: $SKILLS_SOURCE_ROOT"
  exit 1
fi

if [ "$WITH_CONFIG" = "1" ]; then
  mkdir -p "$CONFIG_ROOT"
  if [ -f "$CONFIG_SOURCE" ] && [ ! -f "$CONFIG_TARGET" ]; then
    cp "$CONFIG_SOURCE" "$CONFIG_TARGET"
  fi
fi

if [ -f "$PATCH_SCRIPT" ]; then
  PATCH_RESULT="$(python3 "$PATCH_SCRIPT" --target-root "$TARGET_ROOT" --agent-id "$AGENT_ID")"
  echo "[workking] exec patch: $PATCH_RESULT"
fi

echo "[workking] next: start a new OpenClaw session, then run /workking1 through /workking7"
if [ "$WITH_CONFIG" = "1" ]; then
  echo "[workking] optional config copied to: $CONFIG_TARGET"
fi
