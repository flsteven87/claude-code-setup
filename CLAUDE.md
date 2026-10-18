# CLAUDE.md — User Working Profile

@~/.agents/PROFILE.md

## In Claude Code

Read on demand:

- `~/.claude/references/codex-delegation.md` before dispatching or supervising Codex, or before
  choosing worker models for a fan-out.
- `~/.claude/references/harness.md` when a hook or permission blocks work, or before editing
  settings, hooks, or skill invocation.

Rules:

- `/name` directly invokes a Claude-installed skill. Claude's `disable-model-invocation: true`
  remains its native user-only gate.
- Codex is the implementer for substantial bounded work when it can reach the evidence.
- The `research` skill's background agent is for reading that forms an independent, sizeable
  track; otherwise research directly in this session.
- Surface an OAuth MCP failure immediately and point the user to `/mcp`.
- Claude auto-memory is contextual cache. Open the file or repository evidence before relying on
  it or citing it.
- Add `Co-Authored-By: Claude <session model> <noreply@anthropic.com>` only when Claude materially
  co-authored the commit.
- Playwright MCP resolves a relative `browser_take_screenshot` filename against the project root.
  Pass an absolute scratchpad path to keep screenshots out of the repository, then Read that path.
- Wait on CI, deploys, and logs with `run_in_background` or Monitor; the harness blocks foreground
  `sleep`, so `gh pr checks --watch` also runs in the background.
