#!/usr/bin/env bash
# auto-format.sh — PostToolUse hook for automatic code formatting
#
# Runs project-local formatters after Claude writes/edits files:
#   Python  → uv run ruff format + ruff check --fix
#   Frontend → npx prettier --write (only if locally installed)
#
# Design principles:
#   - Uses project-local tools only (respects Dippy philosophy)
#   - Silent on success, fails gracefully (always exit 0)
#   - npx --no prevents downloading prettier if not in project

INPUT=$(cat)

# Extract file path — handles Write, Edit, and MultiEdit tools
FILE_PATH=$(echo "$INPUT" | jq -r '
  .tool_input.file_path //
  (.tool_input.edits[0].file_path // empty)
')

# No file path or file doesn't exist → skip
[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 0

case "${FILE_PATH##*.}" in
  py)
    uv run ruff format "$FILE_PATH" 2>/dev/null
    uv run ruff check --fix "$FILE_PATH" 2>/dev/null
    ;;
  ts|tsx|js|jsx|css|scss|html|vue)
    npx --no prettier --write "$FILE_PATH" 2>/dev/null || true
    ;;
esac

exit 0
