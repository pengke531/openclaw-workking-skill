#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-$HOME/.openclaw}"
"$(cd "$(dirname "$0")" && pwd)/install-workking-skill.sh" "$TARGET_ROOT"
