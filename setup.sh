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

# bin/codex-reconcile-phantoms.sh is wired as a UserPromptSubmit hook and is invoked
# directly, so bin/ needs the same treatment as hooks/.
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
echo "    claude plugin install code-review@claude-plugins-official"
echo "    claude plugin install typescript-lsp@claude-plugins-official"
echo "    claude plugin install pyright-lsp@claude-plugins-official"
echo "    claude plugin install ralph-loop@claude-plugins-official"
echo "    claude plugin install andrej-karpathy-skills@karpathy-skills"
echo ""
warn "Plugin installation is interactive — Claude Code manages this itself"
echo ""
echo -e "${BOLD}mattpocock-skills is self-hosted, not installed:${RESET}"
echo "  skills/mattpocock-skills/ carries its own manifest and symlinks into the"
echo "  marketplace clone. Installing the plugin makes the skills-dir scan skip it."
echo ""
echo "    claude plugin marketplace add mattpocock/skills   # populates the symlink target"
echo ""
fail_hint="run: claude plugin marketplace add mattpocock/skills"
if [ -d ~/.claude/plugins/marketplaces/mattpocock/skills ]; then
  pass "mattpocock marketplace clone present (symlink target resolves)"
  if uv run python ~/.claude/scripts/reconcile_matt_manifest.py --check --runtime; then
    pass "mattpocock manifest and Claude runtime inventory agree"
  else
    fail "mattpocock manifest or runtime inventory is inconsistent"
    errors=$((errors + 1))
  fi
else
  fail "mattpocock marketplace clone missing — $fail_hint"
  errors=$((errors + 1))
fi

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
  "$HOME/.agents/skills/graph-decide/SKILL.md"
  "$HOME/.agents/skills/graph-deliver/SKILL.md"
  "$HOME/.agents/skills/graph-dispatch/SKILL.md"
  "$HOME/.agents/skills/graph-integrate/SKILL.md"
  "$HOME/.agents/skills/graph-portfolio/SKILL.md"
  "$HOME/.agents/skills/graph-refresh/SKILL.md"
  "$HOME/.agents/skills/graph-run/SKILL.md"
  "$HOME/.agents/skills/graph-ticket/SKILL.md"
  "$HOME/.agents/skills/use-code-review-graph/SKILL.md"
)
for target in "${shared_skill_targets[@]}"; do
  if [ -f "$target" ]; then
    pass "shared skill target present: ${target#"$HOME/"}"
  else
    fail "shared skill target missing: ${target#"$HOME/"} — setup verifies but does not restore shared skills"
    errors=$((errors + 1))
  fi
done

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
