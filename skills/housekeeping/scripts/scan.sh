#!/usr/bin/env bash
# scan.sh — Scan Claude Code artifacts and report housekeeping status
# Usage: bash scan.sh [--project <project-path>]
# If --project is omitted, scans ALL projects under ~/.claude/projects/

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

echo "=========================================="
echo " Claude Code Housekeeping Scan"
echo " $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="

# ─── 1. Global CLAUDE.md ───
echo ""
echo "## 1. Global CLAUDE.md"
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

# ─── 2. Rules directory ───
echo ""
echo "## 2. Rules (~/.claude/rules/)"
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

# ─── 3. Skills inventory ───
echo ""
echo "## 3. User Skills (~/.claude/skills/)"
SKILLS_DIR="${CLAUDE_DIR}/skills"
if [[ -d "$SKILLS_DIR" ]]; then
  SKILL_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  echo "  total: ${SKILL_COUNT} skills"
  # Check for oversized SKILL.md
  find "$SKILLS_DIR" -name "SKILL.md" -type f -exec wc -l {} + 2>/dev/null | \
    while read -r lines path; do
      [[ "$path" == "total" ]] && continue
      skill=$(basename "$(dirname "$path")")
      if (( lines > 500 )); then
        echo "  ⚠️  ${skill}: ${lines} lines (over 500 limit)"
      fi
    done
else
  echo "  (not found)"
fi

# ─── 4. Auto memory per project ───
echo ""
echo "## 4. Auto Memory (per project)"

scan_project_memory() {
  local proj_dir="$1"
  local proj_name=$(basename "$proj_dir")
  local mem_dir="${proj_dir}/memory"

  if [[ ! -d "$mem_dir" ]]; then
    return
  fi

  local mem_files=$(find "$mem_dir" -name "*.md" -type f 2>/dev/null)
  local mem_count=0
  if [[ -n "$mem_files" ]]; then
    mem_count=$(echo "$mem_files" | wc -l | tr -d ' ')
  fi

  if (( mem_count == 0 )); then
    return
  fi

  local total_lines=0
  local stale_files=0
  local now=$(date +%s)

  echo ""
  echo "  ### ${proj_name}"
  echo "  files: ${mem_count}"

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    local fl=$(wc -l < "$f" | tr -d ' ')
    total_lines=$(( total_lines + fl ))
    local fname=$(basename "$f")

    # Check staleness (>30 days since last modification)
    if [[ "$(uname)" == "Darwin" ]]; then
      local mtime=$(stat -f %m "$f" 2>/dev/null || echo 0)
    else
      local mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    fi
    local age_days=$(( (now - mtime) / 86400 ))

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
}

if [[ -n "$TARGET_PROJECT" ]]; then
  # Scan specific project
  proj_encoded=$(echo "$TARGET_PROJECT" | sed 's|/|-|g')
  proj_path="${PROJECTS_DIR}/-${proj_encoded}"
  if [[ -d "$proj_path" ]]; then
    scan_project_memory "$proj_path"
  else
    echo "  Project not found: ${proj_path}"
  fi
else
  # Scan all projects
  for proj_dir in "${PROJECTS_DIR}"/*/; do
    [[ -d "$proj_dir" ]] && scan_project_memory "$proj_dir"
  done
fi

# ─── 5. Stale plans (project-level) ───
echo ""
echo "## 5. Project Plans (*.plan.md, plans/)"
find_plans() {
  local base="$1"
  find "$base" -maxdepth 3 \( -name "*.plan.md" -o -name "PLAN.md" -o -path "*/plans/*.md" \) -type f 2>/dev/null
}

PLAN_COUNT=0
if [[ -n "$TARGET_PROJECT" ]]; then
  PLANS=$(find_plans "$TARGET_PROJECT")
else
  # Search common project directories
  PLANS=$(find ~/Desktop -maxdepth 4 \( -name "*.plan.md" -o -name "PLAN.md" -o -path "*/plans/*.md" \) -type f 2>/dev/null)
fi

while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  PLAN_COUNT=$((PLAN_COUNT + 1))
  lines=$(wc -l < "$p" | tr -d ' ')
  # Check for completion markers
  done_count=$(grep -Ec '\[x\]|✅|COMPLETED|DONE' "$p" 2>/dev/null; true)
  todo_count=$(grep -Ec '\[ \]|TODO|PENDING|IN PROGRESS' "$p" 2>/dev/null; true)
  done_count=${done_count:-0}
  todo_count=${todo_count:-0}
  echo "  📋 ${p}"
  echo "     lines: ${lines} | done: ${done_count} | pending: ${todo_count}"
  if (( todo_count == 0 && done_count > 0 )); then
    echo "     ✅ Appears COMPLETED — safe to archive/delete"
  fi
done <<< "$PLANS"

if (( PLAN_COUNT == 0 )); then
  echo "  (no plan files found)"
fi

# ─── Summary ───
echo ""
echo "=========================================="
echo " Scan complete. Review items marked ⚠️"
echo "=========================================="
