#!/usr/bin/env bash
#
# Mirror Claude skills to Codex via one-way symlinks.
# SSOT: ~/.claude/skills (tracked in claude-code-setup repo)
# Consumer: ~/.codex/skills (symlinks to SSOT)
# Codex .system/ skills are preserved (Codex-distributed).

set -euo pipefail

CLAUDE_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CODEX_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"

if [[ ! -d "$CLAUDE_DIR" ]]; then
  echo "Error: SSOT not found: $CLAUDE_DIR" >&2
  exit 1
fi

mkdir -p "$CODEX_DIR"

should_manage() {
  local name="$1"
  [[ "$name" != ".system" && "$name" != "SKILLS_INDEX.md" && "$name" != "SKILL_REGISTRY.yaml" ]]
}

added=0
relinked=0
retired=0
skipped=0

# Forward pass: ensure every SSOT skill has a consumer symlink
for ssot_path in "$CLAUDE_DIR"/*; do
  [[ -d "$ssot_path" ]] || continue
  [[ -f "$ssot_path/SKILL.md" ]] || continue

  name="$(basename "$ssot_path")"
  should_manage "$name" || continue

  consumer="$CODEX_DIR/$name"

  if [[ -L "$consumer" ]]; then
    if [[ "$(readlink "$consumer")" == "$ssot_path" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
    rm "$consumer"
    ln -s "$ssot_path" "$consumer"
    relinked=$((relinked + 1))
  elif [[ -e "$consumer" ]]; then
    echo "Warning: $consumer exists and is not a symlink; leaving alone" >&2
    continue
  else
    ln -s "$ssot_path" "$consumer"
    added=$((added + 1))
  fi
done

# Reverse pass: retire stale consumer symlinks whose SSOT is gone
for consumer in "$CODEX_DIR"/*; do
  [[ -L "$consumer" ]] || continue
  name="$(basename "$consumer")"
  should_manage "$name" || continue

  if [[ ! -e "$CLAUDE_DIR/$name/SKILL.md" ]]; then
    rm "$consumer"
    retired=$((retired + 1))
  fi
done

echo "sync-skills: added=$added relinked=$relinked retired=$retired unchanged=$skipped"
