#!/usr/bin/env bash
set -euo pipefail

GRAPHIFY_SCRIPT="${HOME}/.codex/bin/graphify-user.py"

if [[ ! -f "$GRAPHIFY_SCRIPT" ]]; then
  exit 0
fi

exec python3 "$GRAPHIFY_SCRIPT" refresh-claude
