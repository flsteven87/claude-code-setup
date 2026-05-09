#!/usr/bin/env bash
# PostToolUse hook for Edit|MultiEdit|Write — refresh the graphify graph
# for the edited file's nearest graph root.
#
# Always exits 0 — never block an edit. Noops silently if:
#   - graphify-user.py is missing
#   - the edited file isn't under any directory containing graphify-out/
#   - the rebuild itself fails (logged elsewhere by graphify-user.py)

GRAPHIFY_SCRIPT="${HOME}/.codex/bin/graphify-user.py"

if [[ ! -f "$GRAPHIFY_SCRIPT" ]]; then
  exit 0
fi

# Hook contract: PostToolUse payload arrives as JSON on stdin.
# Pull the edited file path from tool_input.file_path.
PAYLOAD=$(cat)
FILE_PATH=$(printf '%s' "$PAYLOAD" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    print((d.get("tool_input") or {}).get("file_path", ""))
except Exception:
    pass
' 2>/dev/null)

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Walk up from the edited file to find the nearest dir that owns a graphify-out/.
ROOT="$FILE_PATH"
[[ -f "$ROOT" ]] && ROOT=$(dirname "$ROOT")
while [[ "$ROOT" != "/" && -n "$ROOT" ]]; do
  if [[ -d "$ROOT/graphify-out" ]]; then
    python3 "$GRAPHIFY_SCRIPT" refresh-worker --code-root "$ROOT" >/dev/null 2>&1 || true
    exit 0
  fi
  ROOT=$(dirname "$ROOT")
done

exit 0
