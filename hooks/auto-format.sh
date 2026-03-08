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

# Extract ALL file paths — handles Write, Edit, and MultiEdit tools
# MultiEdit can touch multiple files; process each one
FILE_PATHS=$(echo "$INPUT" | jq -r '
  if .tool_input.file_path then
    .tool_input.file_path
  elif .tool_input.edits then
    .tool_input.edits[].file_path
  else
    empty
  end
' 2>/dev/null)

[[ -z "$FILE_PATHS" ]] && exit 0

while IFS= read -r FILE_PATH; do
  [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && continue
  case "${FILE_PATH##*.}" in
    py)
      uv run ruff format "$FILE_PATH" 2>/dev/null
      uv run ruff check --fix "$FILE_PATH" 2>/dev/null
      ;;
    ts|tsx|js|jsx|css|scss|html|vue)
      npx --no prettier --write "$FILE_PATH" 2>/dev/null || true
      ;;
  esac
done <<< "$FILE_PATHS"

exit 0
