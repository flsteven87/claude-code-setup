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
- **Runtime configuration is authoritative.** Read `~/.codex/config.toml` when the current model or
  effort matters; do not cache their values in agent documents. Use the configured defaults unless
  the user explicitly requests a one-off override supported by the selected surface.
- ⚠️ Do NOT run `/codex:setup --enable-review-gate`.

## Briefing

Brief it cold: paths, line numbers, success criteria. For read-only work say "review only, do not
edit" explicitly — it defaults to `--write`. Never ask a read-only job to run tests or `uv`: its
sandbox denies all writes and the job thrashes on `Operation not permitted`.

## Observability

`status: running` is not evidence of progress. Check `/codex:status <id>` and make a job expected to
run longer than two minutes visible to the user at least every three minutes. More than ten
consecutive minutes without new output or another progress signal means the job is dead: cancel it,
run `codex-hygiene` if needed, and report the failure. Do not retry automatically.

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
