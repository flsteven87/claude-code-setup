#!/usr/bin/env bash
# gather-standup-data.sh — pull yesterday's authored git activity across the three
# NexRex repos for the daily standup. Deterministic, auth-free, fast.
#
# Usage:
#   gather-standup-data.sh                 # default window: yesterday (Mon → back to Fri)
#   gather-standup-data.sh 2026-06-02      # since this date → yesterday
#   gather-standup-data.sh 2026-06-02 2026-06-04   # explicit since → until
#
# Why git-only (no gh): squash-merged PRs keep Steven as the *author*, so
# `git log <remote>/main --author=<email>` on the fetched remote branch already
# catches them — and the PR number lives in the commit subject as "(#NNN)".
# That makes a standup fast and dependency-free. Use gh only if a link needs verifying.

set -uo pipefail

EMAIL="steven.wu@nexrex.ai"   # matches BOTH "Steven Wu" and "steven-wu-nexrex" author names
REPOS=(
  "/Users/po-chi/Desktop/NexRex/nr-platform"
  "/Users/po-chi/Desktop/NexRex/nr-app"
  "/Users/po-chi/Desktop/NexRex/nr-landing"
)

# ---- resolve window ----
if [[ -n "${1:-}" ]]; then
  SINCE="$1"
  UNTIL="${2:-$(date -v-1d +%F)}"
else
  dow=$(date +%u)                 # 1=Mon … 7=Sun
  if [[ "$dow" == "1" ]]; then
    SINCE=$(date -v-3d +%F)       # Monday → reach back to Friday (covers the weekend)
  else
    SINCE=$(date -v-1d +%F)
  fi
  UNTIL=$(date -v-1d +%F)
fi

echo "WINDOW: ${SINCE} 00:00 → ${UNTIL} 23:59   (today=$(date +%F) $(date +%A))"
echo

for repo in "${REPOS[@]}"; do
  name=$(basename "$repo")
  echo "===== ${name} ====="
  if [[ ! -d "$repo/.git" ]]; then
    echo "(not a git repo — skipped)"; echo; continue
  fi

  # Fetch so we see yesterday's merges even when local main is behind (nr-app often is).
  git -C "$repo" fetch --quiet origin 2>/dev/null

  # Resolve the remote default branch (main/master/…); fall back to origin/main.
  ref=$(git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)
  ref=${ref#refs/remotes/}
  [[ -z "$ref" ]] && ref="origin/main"
  echo "(branch: ${ref})"

  log=$(git -C "$repo" log "$ref" --author="$EMAIL" \
        --since="${SINCE} 00:00" --until="${UNTIL} 23:59" \
        --format="%h | %ad | %s" --date=format:'%m-%d %H:%M' --no-merges 2>/dev/null)
  if [[ -z "$log" ]]; then
    echo "(no authored commits in window)"
  else
    echo "$log"
  fi

  stat=$(git -C "$repo" log "$ref" --author="$EMAIL" \
         --since="${SINCE} 00:00" --until="${UNTIL} 23:59" \
         --shortstat --no-merges --format="" 2>/dev/null \
         | grep -E "changed|insert|delet" | head -1)
  [[ -n "$stat" ]] && echo "--- shortstat: ${stat} ---"
  echo
done

echo "NEXT (do via Linear MCP — see SKILL.md Step 2):"
echo "  · 昨天完成 enrich : assignee=me, state=Done,        updatedAt=-P3D, includeArchived=false"
echo "  · 今日重點 候選   : assignee=me, state=\"In Progress\", includeArchived=false"
echo "  · 需要幫忙       : blocked tickets + your open PRs awaiting review"
echo "  · Read MEMORY.md 'Now (...)' section for WIP + blockers already known."
