#!/usr/bin/env bash
# codex-reconcile-phantoms — deterministic liveness reconcile for codex-inline jobs.
#
# WHY THIS EXISTS
# The codex-inline plugin (openai-codex) transitions a job out of "running" only
# when it finishes normally, or at SessionEnd (cleanupSessionJobs in
# scripts/session-lifecycle-hook.mjs). It has NO process-liveness check. So if a
# turn is interrupted / the job process dies while the Claude Code session stays
# OPEN, the job is stuck status="running" forever. The single-active-task guard
# then rejects every later launch in that workspace with
#   "Task <id> is still running. Use /codex:status before continuing it."
# i.e. one dead process poisons the whole workspace for the rest of the session.
#
# This script closes that gap: for every codex-inline job stuck running/queued
# whose pid is NOT alive (kill -0 fails) or is null, it transitions the job to
# "failed" (preserving history — it NEVER deletes), in both state.json and the
# per-job jobs/<id>.json. It NEVER kills a process and NEVER touches the shared
# `codex app-server`, so — unlike codex-hygiene — it is safe to run while other
# Claude Code windows are live.
#
# MODES
#   (default)            reconcile, print one line per cleared phantom
#   --dry-run            report what WOULD be cleared, change nothing
#   --hook               read JSON on stdin (Claude Code hook input); quiet unless
#                        something changed; also warn about a genuinely-live job in
#                        the hook's cwd (helps avoid premature double-fire)
#   --warn-live-cwd DIR  warn if a genuinely-alive job has workspaceRoot==DIR
set -u

STATE_ROOT="${CODEX_INLINE_STATE_ROOT:-$HOME/.claude/plugins/data/codex-inline/state}"
DRY=0
QUIET=0
WARN_CWD=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --hook) QUIET=1 ; HOOK=1 ;;
    --warn-live-cwd) shift; WARN_CWD="${1:-}" ;;
    *) ;;
  esac
  shift
done

command -v jq >/dev/null 2>&1 || { [ "$QUIET" = 1 ] || echo "codex-reconcile: jq not found, skipping"; exit 0; }

# In --hook mode, pull cwd from the hook's stdin JSON so we can warn about a
# live job in the current workspace. Read stdin with a per-line timeout so we
# NEVER block: in production the harness pipes the JSON and closes stdin (returns
# instantly); if stdin is ever left open with no data we bail after ~2s and fall
# back to $PWD instead of hanging until the hook timeout.
if [ "${HOOK:-0}" = 1 ]; then
  _in=""
  _line=""
  while IFS= read -r -t 2 _line; do
    _in="$_in$_line
"
  done
  _in="$_in${_line:-}" # capture a final, newline-less chunk
  if [ -n "$_in" ]; then
    _cwd="$(printf '%s' "$_in" | jq -r '.cwd // empty' 2>/dev/null || true)"
    [ -n "$_cwd" ] && WARN_CWD="$_cwd"
  fi
  [ -z "$WARN_CWD" ] && WARN_CWD="$PWD"
fi

[ -d "$STATE_ROOT" ] || exit 0

now_iso="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
REASON="[reconciled $now_iso: process not alive; stale 'running' job auto-failed by codex-reconcile-phantoms]"
cleared_total=0

is_alive() { # $1 = pid
  case "${1:-}" in
    ''|null|0) return 1 ;;
    *[!0-9]*) return 1 ;;
  esac
  kill -0 "$1" 2>/dev/null
}

for sf in "$STATE_ROOT"/*/state.json; do
  [ -f "$sf" ] || continue
  ws_dir="$(dirname "$sf")"
  ws_name="$(basename "$ws_dir")"

  cand="$(jq -r '.jobs[]? | select(.status=="running" or .status=="queued") | "\(.id)\t\(.pid)"' "$sf" 2>/dev/null || true)"
  [ -z "$cand" ] && continue

  dead_ids=""
  while IFS="$(printf '\t')" read -r jid pid; do
    [ -z "${jid:-}" ] && continue
    if is_alive "$pid"; then
      continue
    fi
    dead_ids="$dead_ids $jid"
  done <<EOF
$cand
EOF

  [ -z "${dead_ids// /}" ] && continue

  for jid in $dead_ids; do
    cleared_total=$((cleared_total + 1))
    if [ "$DRY" = 1 ]; then
      echo "codex-reconcile [DRY]: would clear phantom $jid in $ws_name"
    elif [ "$QUIET" != 1 ]; then
      echo "codex-reconcile: cleared phantom $jid in $ws_name"
    fi
  done

  [ "$DRY" = 1 ] && continue

  ids_json="$(printf '%s\n' $dead_ids | jq -R . | jq -s .)"

  tmp="$sf.reconcile.tmp.$$"
  if jq --argjson ids "$ids_json" --arg now "$now_iso" --arg reason "$REASON" '
    .jobs |= map(
      if (.id as $i | $ids | index($i)) then
        .status = "failed" | .phase = "failed" | .pid = null
        | .completedAt = $now | .updatedAt = $now
        | .errorMessage = ((.errorMessage // "") + (if ((.errorMessage // "") | length) > 0 then " " else "" end) + $reason)
      else . end)
  ' "$sf" > "$tmp" 2>/dev/null; then
    mv "$tmp" "$sf"
  else
    rm -f "$tmp"
    continue
  fi

  for jid in $dead_ids; do
    jf="$ws_dir/jobs/$jid.json"
    [ -f "$jf" ] || continue
    jtmp="$jf.reconcile.tmp.$$"
    if jq --arg now "$now_iso" --arg reason "$REASON" '
      .status = "failed" | .phase = "failed" | .pid = null | .completedAt = $now
      | .errorMessage = ((.errorMessage // "") + (if ((.errorMessage // "") | length) > 0 then " " else "" end) + $reason)
    ' "$jf" > "$jtmp" 2>/dev/null; then
      mv "$jtmp" "$jf"
    else
      rm -f "$jtmp"
    fi
  done
done

if [ "$QUIET" = 1 ] && [ "$cleared_total" -gt 0 ]; then
  echo "codex-reconcile: auto-failed $cleared_total stale 'running' codex job(s) whose process had died — affected workspace(s) are now unblocked for new Codex launches."
fi

# Warn (don't block) about a genuinely-alive job in the current workspace, so the
# operator does not misread a static 'running' chip and fire a duplicate resume.
if [ -n "$WARN_CWD" ]; then
  for sf in "$STATE_ROOT"/*/state.json; do
    [ -f "$sf" ] || continue
    live="$(jq -r --arg cwd "$WARN_CWD" '.jobs[]? | select((.status=="running" or .status=="queued") and .workspaceRoot==$cwd) | "\(.id)\t\(.pid)\t\(.updatedAt // .startedAt)"' "$sf" 2>/dev/null || true)"
    [ -z "$live" ] && continue
    while IFS="$(printf '\t')" read -r jid pid upd; do
      [ -z "${jid:-}" ] && continue
      if is_alive "$pid"; then
        echo "⚠️ codex: a LIVE job ($jid, pid $pid, last update $upd) is already running in $WARN_CWD. Do NOT fire another Codex Resume/rescue — check /codex:status or wait for it to finish."
      fi
    done <<EOF2
$live
EOF2
  done
fi

exit 0
