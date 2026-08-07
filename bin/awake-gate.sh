#!/bin/bash
# awake-gate — keep the Mac awake (lid closed, battery or AC) exactly while
# Claude sessions are working, and restore normal sleep the moment they stop.
#
# usage:
#   awake-gate.sh acquire   < hook-json    session started a turn  -> hold the flag
#   awake-gate.sh release   < hook-json    session finished a turn -> drop its hold
#   awake-gate.sh sweep                    reconcile only (launchd safety net)
#
# One token file per active session in TOKEN_DIR. The kernel SleepDisabled flag
# is on iff at least one token survives the sweep, so concurrent sessions cannot
# switch each other off. Wired into settings.json on UserPromptSubmit / Stop /
# StopFailure / SessionEnd, and to a 5-minute launchd sweep.
#
# Never fails a hook: every path exits 0 and writes nothing to stdout, since
# UserPromptSubmit stdout would be injected into the model's context.

set -uo pipefail

TOKEN_DIR="$HOME/.claude/run/awake"
PMSET=/usr/bin/pmset
# A session process that has not fired a hook in this long is presumed dead.
STALE_MINUTES=720

mkdir -p "$TOKEN_DIR"

# Drop tokens whose session can no longer be running. The `manual` token is the
# hold placed by `awake on`; it answers to the user, not to session lifecycle,
# so it is never swept.
sweep() {
  # Claude Code gone entirely (app quit, crash, force-quit) -> nothing can hold.
  if ! pgrep -f 'claude-code/.*/MacOS/claude' >/dev/null 2>&1; then
    find "$TOKEN_DIR" -type f ! -name manual -delete 2>/dev/null
    return
  fi
  find "$TOKEN_DIR" -type f ! -name manual -mmin "+$STALE_MINUTES" -delete 2>/dev/null
}

# Drive the kernel flag from the surviving token count.
apply() {
  local want=0
  [ -n "$(find "$TOKEN_DIR" -type f -print -quit 2>/dev/null)" ] && want=1
  [ "$($PMSET -g | awk '/SleepDisabled/{print $2}')" = "$want" ] && return
  sudo -n "$PMSET" -a disablesleep "$want" 2>/dev/null
}

session_id() {
  sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

case "${1:-}" in
  acquire)
    sid="$(session_id)"
    sweep
    touch "$TOKEN_DIR/${sid:-unknown}"
    apply
    ;;
  release)
    sid="$(session_id)"
    rm -f "$TOKEN_DIR/${sid:-unknown}"
    sweep
    apply
    ;;
  sweep)
    sweep
    apply
    ;;
esac

exit 0
