#!/usr/bin/env bash
# update-all.sh — single-command refresh of the Claude Code stack
# Usage: ~/.claude/bin/update-all.sh
set -e

echo "▶ 1/7  Claude CLI"
claude update 2>&1 | grep -E "(Current|Successfully|already)" || true

echo
marketplaces=$(find "$HOME/.claude/plugins/marketplaces" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
echo "▶ 2/7  Plugin marketplaces (${marketplaces:-0} configured)"
claude plugin marketplace update 2>&1 | tail -3


echo
echo "▶ 3/7  Plugins"
claude plugin list 2>/dev/null | awk '/^  ❯ /{print $2}' | while read -r p; do
  out=$(claude plugin update "$p" 2>&1 | tail -1)
  echo "  $p — ${out#✔ }"
done

echo
echo "▶ 4/7  Codex CLI and marketplaces"
# Codex is a standalone install owned by an Orca account home; its updater must
# run under that home, and an npm install would add a second, shadowing copy.
codex_link=$(readlink "$HOME/.local/bin/codex" 2>/dev/null || true)
case "$codex_link" in
  */packages/standalone/current/bin/codex)
    CODEX_HOME="${codex_link%/packages/standalone/current/bin/codex}" "$HOME/.local/bin/codex" update 2>&1 | tail -3 ;;
  *)
    echo "  codex is not the standalone install; update it through its owner" ;;
esac
codex plugin marketplace upgrade 2>&1 | tail -1

echo
echo "▶ 5/7  Python tools (uv)"
uv tool upgrade --all 2>&1 | tail -5 || true
echo "  npx + uvx-based MCP servers (@latest tags) auto-refresh on next launch"

echo
echo "▶ 6/7  External skills (~/.agents; one chore(skills) commit when clean)"
uv run --no-project --with pyyaml python "$HOME/.agents/scripts/update_external_skills.py" --commit \
  || echo "  needs review: resolve the needs_human items above, then commit in ~/.agents"
bash "$HOME/.claude/setup.sh" 2>&1 | grep -E "shared skill linked|dangling|conflicts" | grep -v "✓ shared skill linked" || true

echo
echo "▶ 7/7  Sync ~/.claude/bin/ → ~/.local/bin/ (PATH entry)"
mkdir -p "$HOME/.local/bin"
for src in "$HOME/.claude/bin/"*; do
  [ -f "$src" ] || continue
  name=$(basename "$src")
  [ "$name" = "update-all.sh" ] && continue
  dest="$HOME/.local/bin/$name"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    echo "  $name — already linked"
  else
    ln -sfn "$src" "$dest"
    echo "  $name — symlinked"
  fi
done

echo
echo "✅ Update complete. Restart any open 'claude' sessions to pick up plugin updates."
