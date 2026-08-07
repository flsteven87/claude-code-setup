#!/bin/zsh

set -u
setopt pipefail
umask 077

readonly BASE_DIR="/Users/po-chi/.claude/automations/daily-dev-update"
readonly PROMPT_FILE="$BASE_DIR/PROMPT.md"
readonly RESULT_DIR="$BASE_DIR/results"
readonly LOG_DIR="$BASE_DIR/logs"
readonly LOCK_DIR="$BASE_DIR/.run.lock"
readonly CODEX_BIN="/Users/po-chi/.local/bin/codex"
readonly RUN_STAMP="$(date '+%Y%m%dT%H%M%S%z')"
readonly STARTED_AT="$(date -Iseconds)"
readonly RUN_LOG="$LOG_DIR/run-$RUN_STAMP.log"
readonly RUN_RESULT="$RESULT_DIR/result-$RUN_STAMP.md"
readonly TEMP_RESULT="$RESULT_DIR/.result-$RUN_STAMP.tmp"
readonly TEMP_STATUS="$RESULT_DIR/.status-$RUN_STAMP.tmp"

mkdir -p "$RESULT_DIR" "$LOG_DIR"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  print -r -- "Another daily development-tool update is already running." >&2
  exit 75
fi

print -r -- "$$" > "$LOCK_DIR/pid"
cleanup() {
  rm -f "$LOCK_DIR/pid"
  rmdir "$LOCK_DIR" 2>/dev/null || true
  rm -f "$TEMP_RESULT" "$TEMP_STATUS"
}
trap cleanup EXIT INT TERM HUP

if [[ ! -x "$CODEX_BIN" ]]; then
  print -r -- "Codex executable is missing: $CODEX_BIN" >&2
  exit 127
fi

if [[ ! -r "$PROMPT_FILE" ]]; then
  print -r -- "Updater prompt is missing: $PROMPT_FILE" >&2
  exit 66
fi

export CODEX_HOME="/Users/po-chi/.codex"
export HOME="/Users/po-chi"
export CI=1
export NONINTERACTIVE=1
export HOMEBREW_NO_ENV_HINTS=1
export PNPM_HOME="/Users/po-chi/Library/pnpm"
NVM_NODE_BIN="$(find /Users/po-chi/.nvm/versions/node -mindepth 2 -maxdepth 2 -type d -name bin 2>/dev/null | sort -V | tail -n 1)"
export PATH="${NVM_NODE_BIN:+$NVM_NODE_BIN:}$PNPM_HOME/bin:/Users/po-chi/.local/bin:/Users/po-chi/.cargo/bin:/Users/po-chi/.bun/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

{
  print -r -- "[$STARTED_AT] Starting unattended daily development-tool update."
  print -r -- "Codex: $($CODEX_BIN --version 2>/dev/null || print unknown)"
} >> "$RUN_LOG"

"$CODEX_BIN" \
  --ask-for-approval never \
  --sandbox danger-full-access \
  --search \
  exec \
  --ignore-user-config \
  --skip-git-repo-check \
  --ephemeral \
  --color never \
  --model gpt-5.6-sol \
  --config 'model_reasoning_effort="medium"' \
  --cd "/Users/po-chi" \
  --output-last-message "$TEMP_RESULT" \
  - < "$PROMPT_FILE" >> "$RUN_LOG" 2>&1 &

readonly CODEX_PID=$!
(
  sleep 10800
  if kill -0 "$CODEX_PID" 2>/dev/null; then
    print -r -- "Updater exceeded the three-hour limit; terminating PID $CODEX_PID." >> "$RUN_LOG"
    kill -TERM "$CODEX_PID" 2>/dev/null || true
    sleep 10
    kill -KILL "$CODEX_PID" 2>/dev/null || true
  fi
) &
readonly WATCHDOG_PID=$!

wait "$CODEX_PID"
EXIT_CODE=$?
kill "$WATCHDOG_PID" 2>/dev/null || true
wait "$WATCHDOG_PID" 2>/dev/null || true

readonly FINISHED_AT="$(date -Iseconds)"
if [[ -s "$TEMP_RESULT" ]]; then
  mv "$TEMP_RESULT" "$RUN_RESULT"
else
  print -r -- "更新工作未產生最終報告；請檢查 $RUN_LOG。" > "$RUN_RESULT"
fi

cp "$RUN_RESULT" "$RESULT_DIR/latest.md"
jq -n \
  --arg startedAt "$STARTED_AT" \
  --arg finishedAt "$FINISHED_AT" \
  --arg report "$RUN_RESULT" \
  --arg log "$RUN_LOG" \
  --argjson exitCode "$EXIT_CODE" \
  '{startedAt:$startedAt,finishedAt:$finishedAt,exitCode:$exitCode,report:$report,log:$log}' \
  > "$TEMP_STATUS"
mv "$TEMP_STATUS" "$RESULT_DIR/latest.json"

print -r -- "[$FINISHED_AT] Update finished with exit code $EXIT_CODE." >> "$RUN_LOG"
exit "$EXIT_CODE"
