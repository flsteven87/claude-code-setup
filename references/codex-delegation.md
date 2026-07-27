# Codex Delegation Reference

> Moved out of CLAUDE.md 2026-07-26 (progressive disclosure). **Read this before dispatching any
> Codex job.** CLAUDE.md keeps only the routing decision; the mechanics live here.

## What goes where

- **Hand to Codex:** implementing a finalized plan; mechanical refactors/migrations once the target
  shape is clear; write-capable simplify/refactor passes on changed code; independent code-quality
  reads; root-cause investigation when Claude Code is stuck after one or two passes.
- **Keep in Claude Code:** brainstorming, plan writing, architectural review, cross-file synthesis,
  multi-source research, ticket structuring, strategy, conversation steering.

## Mechanism

- Read-only review → `/codex:review --background` or `/codex:adversarial-review --background`.
- Write-capable rescue → `Agent(subagent_type: "codex:codex-rescue", prompt: "...")` with
  `run_in_background=true` **on the Agent tool itself**. Never pass `--background` inside the prompt
  and never pair it with `isolation: "worktree"` — both kill Codex early.
- **Model is config-owned.** `~/.codex/config.toml` pins `gpt-5.6-sol` + `model_reasoning_effort =
  "xhigh"`; every surface (review / adversarial-review / rescue / `codex` MCP) inherits it. Never
  pass `--model` / `--effort` at a call site — `review/start` has no effort param, so it drifts.
- ⚠️ Do NOT run `/codex:setup --enable-review-gate`.

## Briefing

Brief it cold: paths, line numbers, success criteria. For read-only work say "review only, do not
edit" explicitly — it defaults to `--write`. Never ask a read-only job to run tests or `uv`: its
sandbox denies all writes and the job thrashes on `Operation not permitted`.

## Observability

`status: running` ≠ progress — check `/codex:status <id>`. Frozen `progressPreview` ~5 min AND
elapsed > 10 min → dead: `/codex:cancel <id>`, `codex-hygiene`, retry. Always auto-poll jobs expected
to run > 5 min with `/loop 90s /codex:status <id>`.

`codex-hygiene` exits 1 and changes nothing while any job is still alive — cancel first, that is why
the order above is what it is. If the job is only *stuck* rather than wedged (status pinned to
"running" after its process died, blocking new launches), `codex-reconcile-phantoms.sh` clears it
without killing anything.

## Adversarial review angles

Brief read-only with the diff or plan plus one angle:

**end-state alignment** · auth bypass · data loss · rollback safety · race conditions ·
degraded dependencies · version skew · observability gaps

**End-state alignment is the mandatory first angle for a plan or spec** — the other seven are
implementation-risk angles that judge a plan on its own framing. `/reverse-thinking` is the full
method (distill end state → back-derive preconditions → check against codebase reality) and is what
to run inline when Codex is unavailable.
