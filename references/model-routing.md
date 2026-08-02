# Multi-Agent Model Routing Reference

> Moved out of CLAUDE.md 2026-07-26 (progressive disclosure). **Read this before authoring a
> workflow or spawning a fan-out of agents.** CLAUDE.md keeps only the role→model table.

## Why worker tier dominates

Claude-native workers **inherit the session model unless routed down**. Worker-tier choice drives
~5× more total cost than orchestrator-tier choice — the leverage is cheap workers, not a cheap
orchestrator. Multi-agent is not inherently cheaper; the savings come only from routing cheap roles
to cheap models.

**Code review is the one role this argument does not reach**, and it is routed *sideways*, not down.
The implementer is Opus 5, so any Opus reviewer is the same mind re-reading its own diff — the tier
is right but the independence is missing. Send it to Codex, whose different training gives it
different blind spots; fall back to `opus` only when the review needs data Codex cannot reach.

Never below that. Judging whether a diff is correct is as hard as writing it, so a cheap reviewer
returns confident wrong findings, and every one still has to be read and dismissed by the expensive
tier. Take the savings from the `haiku` scan/search rows and the mechanical gate rows, which is where
they actually were. This binds a workflow's adversarial-verify stage whenever the claims under test
are about code; verifying research claims against sources is a different job and stays on `sonnet`.

## Rules

- **Pin every workflow stage's `model`.** A workflow's `agent()` calls inherit the session model; an
  un-routed workflow bills every agent (up to 1000) at the session tier — the #1 cost blowout.
- Use `opts.effort: 'low'` for mechanical stages when the in-session Workflow tool exposes it.
- **`Workflow({name: ...})` is banned** — a PreToolUse hook (`workflow_route_guard.py`) denies it,
  because named/built-in workflows ship with zero routing. Even when a skill's instructions say to
  invoke by name, that is not an exemption: use the routed copy in `~/.claude/workflows/` via
  `scriptPath`.
- **Never** set `settings.json "model": "fable"` or a global `CLAUDE_CODE_SUBAGENT_MODEL` — both
  defeat per-role routing.
- `fable` at the orchestrator tier is for hard, long-horizon async fan-out only — never as a
  baseline, never in `settings.json`.
