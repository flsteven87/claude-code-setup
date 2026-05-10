#!/usr/bin/env bash
# update-all.sh — single-command refresh of the Claude Code stack
# Usage: ~/.claude/bin/update-all.sh
set -e

echo "▶ 1/5  Claude CLI"
claude update 2>&1 | grep -E "(Current|Successfully|already)" || true

echo
echo "▶ 2/5  Plugin marketplaces (5 configured)"
claude plugin marketplace update 2>&1 | tail -3

echo
echo "▶ 3/5  Plugins"
claude plugin list 2>/dev/null | awk '/^  ❯ /{print $2}' | while read -r p; do
  out=$(claude plugin update "$p" 2>&1 | tail -1)
  echo "  $p — ${out#✔ }"
done

echo
echo "▶ 4/5  Codex CLI"
npm install -g @openai/codex@latest 2>&1 | tail -3

echo
echo "▶ 5/5  Python tools (uv) + npx cache hint"
uv tool upgrade --all 2>&1 | tail -5 || true
echo "  npx + uvx-based MCP servers (@latest tags) auto-refresh on next launch"
echo "  serena/uv: ran 'uv cache prune' previously — refreshes on next uvx call"

echo
echo "✅ Update complete. Restart any open 'claude' sessions to pick up plugin updates."
