#!/usr/bin/env bash
set -euo pipefail

# Claude Code Setup — one-time configuration for this dotfiles repo
# Safe to run multiple times (idempotent)

BOLD='\033[1m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

pass() { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${YELLOW}!${RESET} $1"; }
fail() { echo -e "  ${RED}✗${RESET} $1"; }

echo -e "${BOLD}Claude Code Setup${RESET}"
echo ""

# --- Prerequisites ---
echo -e "${BOLD}Checking prerequisites...${RESET}"

if command -v claude &>/dev/null; then
  pass "Claude Code CLI found"
else
  fail "Claude Code CLI not found — install from https://claude.ai/code"
  exit 1
fi

if command -v uv &>/dev/null; then
  pass "uv found"
else
  fail "uv not found — install from https://docs.astral.sh/uv/"
  exit 1
fi

# --- Bash gate ---
echo ""
echo -e "${BOLD}Checking the Bash gate...${RESET}"

# Deletions are redirected to `trash` rather than gated behind a prompt, so the
# binary has to exist. macOS 14+ ships it at /usr/bin/trash.
if command -v trash &>/dev/null; then
  pass "trash found — hooks/pre_bash_guard.py can redirect rm to it"
else
  warn "trash not found — pre_bash_guard.py will still deny rm, but with no working alternative"
fi

# --- Hooks ---
echo ""
echo -e "${BOLD}Verifying hooks and scripts are executable...${RESET}"

# bin/ scripts are invoked directly, so they need the same treatment as hooks/.
for script in ~/.claude/hooks/*.sh ~/.claude/bin/*; do
  # Skip symlinks: update-all.sh links bin/* out to ~/.local/bin, and chmod would
  # follow a link to a target this script has no business touching.
  [ -L "$script" ] && continue
  [ -f "$script" ] || continue
  if [ -x "$script" ]; then
    pass "$(basename "$script") is executable"
  else
    chmod +x "$script"
    pass "$(basename "$script") made executable"
  fi
done

# --- Plugins ---
echo ""
echo -e "${BOLD}Plugins to install:${RESET}"
errors=0
echo "  Run these inside Claude Code or via CLI:"
echo ""
echo "    claude plugin install codex@openai-codex"
echo "    claude plugin install typescript-lsp@claude-plugins-official"
echo "    claude plugin install pyright-lsp@claude-plugins-official"
echo ""
warn "Plugin installation is interactive — Claude Code manages this itself"
echo ""

# --- Verify ---
echo ""
echo -e "${BOLD}Verification...${RESET}"

if ! git -C ~/.claude cat-file -e :settings.json 2>/dev/null; then
  fail "tracked settings.json is unavailable from the Git index"
  errors=$((errors + 1))
elif git -C ~/.claude show :settings.json | grep -q '/Users/'; then
  fail "tracked settings.json contains hardcoded /Users/ paths"
  errors=$((errors + 1))
else
  pass "tracked settings.json paths are portable"
fi

shared_skill_targets=(
  "$HOME/.agents/skills/ship/SKILL.md"
  "$HOME/.agents/skills/catchup/SKILL.md"
  "$HOME/.agents/skills/handoff/SKILL.md"
  "$HOME/.agents/skills/git-converge-main/SKILL.md"
  "$HOME/.agents/skills/use-code-review-graph/SKILL.md"
  "$HOME/.agents/skills/milestone-dispatch/SKILL.md"
  "$HOME/.agents/skills/topics/SKILL.md"
  "$HOME/.agents/skills/codebase-design/SKILL.md"
  "$HOME/.agents/skills/orca-cli/SKILL.md"
  "$HOME/.agents/skills/strategy-review/SKILL.md"
  "$HOME/.agents/skills/audit-pr-topics/SKILL.md"
  "$HOME/.agents/skills/reverse-thinking/SKILL.md"
  "$HOME/.agents/skills/wayfinder/SKILL.md"
)
for target in "${shared_skill_targets[@]}"; do
  if [ -f "$target" ]; then
    pass "shared skill target present: ${target#"$HOME/"}"
  else
    fail "shared skill target missing: ${target#"$HOME/"} — setup verifies but does not restore shared skills"
    errors=$((errors + 1))
  fi
done

# Every shared skill in ~/.agents/skills is linked for Claude, except the names listed (with
# reasons) in ~/.agents/skills/.claude-skip.
skip_file="$HOME/.agents/skills/.claude-skip"
if [ -f "$skip_file" ]; then
  claude_excluded_skills=" $(grep -v '^#' "$skip_file" | tr '\n' ' ') "
else
  fail "missing ${skip_file#"$HOME/"} — restore ~/.agents before linking skills"
  errors=$((errors + 1))
  claude_excluded_skills=" "
fi
mkdir -p "$HOME/.claude/skills"
for target_dir in "$HOME"/.agents/skills/*/; do
  name=$(basename "$target_dir")
  [ -f "$target_dir/SKILL.md" ] || continue
  case "$claude_excluded_skills" in *" $name "*) continue ;; esac
  link_path="$HOME/.claude/skills/$name"
  if [ -L "$link_path" ] && [ "$link_path" -ef "$target_dir" ]; then
    pass "shared skill linked: skills/$name"
  elif [ -e "$link_path" ] || [ -L "$link_path" ]; then
    fail "skill path conflicts: skills/$name — expected a link to ~/.agents/skills/$name"
    errors=$((errors + 1))
  else
    ln -s "../../.agents/skills/$name" "$link_path"
    pass "shared skill linked: skills/$name"
  fi
done
for link_path in "$HOME"/.claude/skills/*; do
  if [ -L "$link_path" ] && [ ! -e "$link_path" ]; then
    fail "dangling skill link: skills/$(basename "$link_path")"
    errors=$((errors + 1))
  fi
done

# Refero establishes the frontend baseline; Impeccable supplies refinement and quality checks.
# Its Claude copy, subagents, and detector hook come from the upstream release bundle,
# so setup verifies them but does not restore them.
impeccable_dir="$HOME/.claude/skills/impeccable"
impeccable_version() { sed -n 's/^ *version: //p' "$1/SKILL.md" 2>/dev/null | head -1; }
if [ -x "$impeccable_dir/scripts/impeccable" ] \
  && [ -n "$(impeccable_version "$impeccable_dir")" ] \
  && [ "$(impeccable_version "$impeccable_dir")" = "$(impeccable_version "$HOME/.agents/skills/impeccable")" ]; then
  pass "Impeccable Claude copy matches ~/.agents ($(impeccable_version "$impeccable_dir"))"
else
  fail "Impeccable Claude copy is missing or differs from ~/.agents/skills/impeccable — reinstall the same release for Claude"
  errors=$((errors + 1))
fi
for name in asset-producer documenter finish-reviewer manual-edit-applier; do
  if [ -f "$HOME/.claude/agents/impeccable-$name.md" ]; then
    pass "Impeccable subagent present: agents/impeccable-$name.md"
  else
    fail "Impeccable subagent missing: agents/impeccable-$name.md — copy .claude/agents/ from the installed release"
    errors=$((errors + 1))
  fi
done
# A hook in ~/.claude/settings.local.json only applies when $HOME is the project.
if grep -q 'skills/impeccable/scripts/impeccable' ~/.claude/settings.json; then
  pass "Impeccable detector hook registered at user scope"
else
  fail "Impeccable detector hook absent from ~/.claude/settings.json — UI edits in other projects go unchecked"
  errors=$((errors + 1))
fi

if [ -f ~/.claude/hooks/auto-format.sh ] && [ -x ~/.claude/hooks/auto-format.sh ]; then
  pass "Hooks are in place"
else
  fail "Hook scripts missing or not executable"
  errors=$((errors + 1))
fi

# The Bash gate is the only thing standing between the agent and an unrecoverable
# deletion, so a syntax error in it must fail setup rather than fail open.
if uv run ~/.claude/hooks/pre_bash_guard.py <<<'{"tool_name":"Bash","tool_input":{"command":"rm -rf /Users/x/work"}}' | grep -q '"deny"'; then
  pass "pre_bash_guard.py is denying deletions"
else
  fail "pre_bash_guard.py did not deny a test rm — the Bash gate is open"
  errors=$((errors + 1))
fi

echo ""
if [ "$errors" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}Setup complete!${RESET} Launch Claude Code with: ${BOLD}claude${RESET}"
else
  echo -e "${RED}${BOLD}Setup finished with $errors error(s).${RESET} Fix the issues above and re-run."
  exit 1
fi
