#!/usr/bin/env bash
# scan.sh — Scan Claude Code artifacts for the CURRENT repo only
# Usage: bash scan.sh [--project <project-path>]
# If --project is omitted, auto-detects from git root of CWD

set -o pipefail

CLAUDE_DIR="${HOME}/.claude"
PROJECTS_DIR="${CLAUDE_DIR}/projects"
TARGET_PROJECT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) TARGET_PROJECT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Auto-detect current project from git root
if [[ -z "$TARGET_PROJECT" ]]; then
  GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  if [[ -n "$GIT_ROOT" ]]; then
    TARGET_PROJECT="$GIT_ROOT"
  else
    TARGET_PROJECT="$(pwd)"
  fi
fi

# Encode project path for Claude's directory naming convention
proj_encoded=$(echo "$TARGET_PROJECT" | sed 's|/|-|g')
PROJ_MEMORY_DIR="${PROJECTS_DIR}/${proj_encoded}/memory"

echo "=========================================="
echo " Claude Code Housekeeping Scan"
echo " $(date '+%Y-%m-%d %H:%M')"
echo " Project: ${TARGET_PROJECT}"
echo "=========================================="

# ─── 1. Project CLAUDE.md ───
echo ""
echo "## 1. Project CLAUDE.md"
PROJECT_MD="${TARGET_PROJECT}/CLAUDE.md"
if [[ -f "$PROJECT_MD" ]]; then
  LINES=$(wc -l < "$PROJECT_MD" | tr -d ' ')
  SIZE=$(wc -c < "$PROJECT_MD" | tr -d ' ')
  echo "  path:  ${PROJECT_MD}"
  echo "  lines: ${LINES}"
  echo "  size:  $(( SIZE / 1024 ))KB"
  if (( LINES > 200 )); then
    echo "  ⚠️  OVER 200 lines — consider splitting"
  else
    echo "  ✅ Size OK"
  fi
else
  echo "  (not found)"
fi

# ─── 2. Global CLAUDE.md ───
echo ""
echo "## 2. Global CLAUDE.md"
GLOBAL_MD="${CLAUDE_DIR}/CLAUDE.md"
if [[ -f "$GLOBAL_MD" ]]; then
  LINES=$(wc -l < "$GLOBAL_MD" | tr -d ' ')
  SIZE=$(wc -c < "$GLOBAL_MD" | tr -d ' ')
  echo "  path:  ${GLOBAL_MD}"
  echo "  lines: ${LINES}"
  echo "  size:  $(( SIZE / 1024 ))KB"
  if (( LINES > 200 )); then
    echo "  ⚠️  OVER 200 lines — consider splitting into .claude/rules/"
  else
    echo "  ✅ Size OK"
  fi
else
  echo "  (not found)"
fi

# ─── 3. Rules directory ───
echo ""
echo "## 3. Rules (~/.claude/rules/)"
RULES_DIR="${CLAUDE_DIR}/rules"
if [[ -d "$RULES_DIR" ]]; then
  RULE_COUNT=$(find "$RULES_DIR" -name "*.md" -type f | wc -l | tr -d ' ')
  echo "  files: ${RULE_COUNT}"
  find "$RULES_DIR" -name "*.md" -type f -exec wc -l {} + 2>/dev/null | \
    while read -r lines path; do
      [[ "$path" == "total" ]] && continue
      name=$(basename "$path")
      if (( lines > 100 )); then
        echo "  ⚠️  ${name}: ${lines} lines (consider splitting)"
      else
        echo "  ✅ ${name}: ${lines} lines"
      fi
    done
else
  echo "  (not found)"
fi

# ─── 4. Auto Memory (current project only) ───
echo ""
echo "## 4. Auto Memory"

if [[ -d "$PROJ_MEMORY_DIR" ]]; then
  mem_files=$(find "$PROJ_MEMORY_DIR" -name "*.md" -type f 2>/dev/null)
  mem_count=0
  if [[ -n "$mem_files" ]]; then
    mem_count=$(echo "$mem_files" | wc -l | tr -d ' ')
  fi

  if (( mem_count > 0 )); then
    echo "  dir:   ${PROJ_MEMORY_DIR}"
    echo "  files: ${mem_count}"

    total_lines=0
    stale_files=0
    now=$(date +%s)

    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      fl=$(wc -l < "$f" | tr -d ' ')
      total_lines=$(( total_lines + fl ))
      fname=$(basename "$f")

      if [[ "$(uname)" == "Darwin" ]]; then
        mtime=$(stat -f %m "$f" 2>/dev/null || echo 0)
      else
        mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
      fi
      age_days=$(( (now - mtime) / 86400 ))

      if (( age_days > 30 )); then
        echo "  ⚠️  STALE (${age_days}d): ${fname} — ${fl} lines"
        stale_files=$((stale_files + 1))
      elif (( fl > 100 )); then
        echo "  🟡 LARGE: ${fname} — ${fl} lines"
      else
        echo "  ✅ ${fname} — ${fl} lines (${age_days}d ago)"
      fi
    done <<< "$mem_files"

    echo "  total lines: ${total_lines}"
    if (( total_lines > 200 )); then
      echo "  ⚠️  Combined memory exceeds 200 lines — consider consolidating"
    fi
    if (( stale_files > 0 )); then
      echo "  ⚠️  ${stale_files} stale file(s) (>30d) — review for removal"
    fi
  else
    echo "  (no memory files)"
  fi
else
  echo "  (no memory directory)"
fi

# ─── 5. Project Plans (current project only) ───
echo ""
echo "## 5. Project Plans"

PLANS=$(find "$TARGET_PROJECT" -maxdepth 3 \( -name "*.plan.md" -o -name "PLAN.md" -o -path "*/plans/*.md" \) -type f 2>/dev/null)
PLAN_COUNT=0

while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  PLAN_COUNT=$((PLAN_COUNT + 1))
  lines=$(wc -l < "$p" | tr -d ' ')
  done_count=$(grep -Ec '\[x\]|✅|COMPLETED|DONE' "$p" 2>/dev/null; true)
  todo_count=$(grep -Ec '\[ \]|TODO|PENDING|IN PROGRESS' "$p" 2>/dev/null; true)
  done_count=${done_count:-0}
  todo_count=${todo_count:-0}
  # Show path relative to project root
  rel_path="${p#$TARGET_PROJECT/}"
  echo "  📋 ${rel_path}"
  echo "     lines: ${lines} | done: ${done_count} | pending: ${todo_count}"
  if (( todo_count == 0 && done_count > 0 )); then
    echo "     ✅ Appears COMPLETED — safe to archive/delete"
  fi
done <<< "$PLANS"

if (( PLAN_COUNT == 0 )); then
  echo "  (no plan files found)"
fi

# ─── 6. Stale docs check ───
echo ""
echo "## 6. Docs Overview"
if [[ -d "${TARGET_PROJECT}/docs" ]]; then
  doc_dirs=$(find "${TARGET_PROJECT}/docs" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  while IFS= read -r d; do
    [[ -z "$d" ]] && continue
    dir_name=$(basename "$d")
    file_count=$(find "$d" -type f -name "*.md" | wc -l | tr -d ' ')
    echo "  📁 docs/${dir_name}/ — ${file_count} files"
  done <<< "$doc_dirs"
else
  echo "  (no docs/ directory)"
fi

# ─── Summary ───
echo ""
echo "=========================================="
echo " Scan complete. Review items marked ⚠️"
echo "=========================================="
