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
echo -e "${BOLD}Verifying hooks are executable...${RESET}"

for hook in ~/.claude/hooks/*.sh; do
  if [ -x "$hook" ]; then
    pass "$(basename "$hook") is executable"
  else
    chmod +x "$hook"
    pass "$(basename "$hook") made executable"
  fi
done

# --- Plugins ---
echo ""
echo -e "${BOLD}Plugins to install:${RESET}"
echo "  Run these inside Claude Code or via CLI:"
echo ""
echo "    claude plugin install superpowers@superpowers-marketplace"
echo "    claude plugin install frontend-design@claude-plugins-official"
echo "    claude plugin install typescript-lsp@claude-plugins-official"
echo "    claude plugin install discord@claude-plugins-official"
echo ""
warn "Plugin installation is interactive — Claude Code manages this itself"

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
