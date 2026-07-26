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

# --- Dippy ---
echo ""
echo -e "${BOLD}Setting up Dippy (Bash command gatekeeper)...${RESET}"

if command -v dippy &>/dev/null; then
  pass "Dippy already installed"
else
  echo "  Installing dippy via uv..."
  uv tool install dippy
  pass "Dippy installed"
fi

if [ -f ~/.dippy/config ]; then
  warn "~/.dippy/config already exists — skipping (compare with dippy/config if needed)"
else
  mkdir -p ~/.dippy
  cp ~/.claude/dippy/config ~/.dippy/config
  pass "Dippy config copied to ~/.dippy/config"
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
else
  warn "mattpocock marketplace clone missing — $fail_hint"
fi

# --- Verify ---
echo ""
echo -e "${BOLD}Verification...${RESET}"

errors=0

if grep -q '/Users/' ~/.claude/settings.json 2>/dev/null; then
  fail "settings.json contains hardcoded /Users/ paths"
  errors=$((errors + 1))
else
  pass "settings.json paths are portable"
fi

if [ -f ~/.dippy/config ]; then
  pass "Dippy config present"
else
  fail "Dippy config missing at ~/.dippy/config"
  errors=$((errors + 1))
fi

if [ -f ~/.claude/hooks/auto-format.sh ] && [ -x ~/.claude/hooks/auto-format.sh ]; then
  pass "Hooks are in place"
else
  fail "Hook scripts missing or not executable"
  errors=$((errors + 1))
fi

echo ""
if [ "$errors" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}Setup complete!${RESET} Launch Claude Code with: ${BOLD}claude${RESET}"
else
  echo -e "${RED}${BOLD}Setup finished with $errors error(s).${RESET} Fix the issues above and re-run."
  exit 1
fi
