# Codex Delegation Reference

Read this before dispatching any Codex job or choosing worker models for a fan-out. CLAUDE.md keeps
the routing decision; the mechanics live here.

## What goes where

- **Hand to Codex:** implementing a finalized plan; mechanical refactors or migrations once the
  target shape is clear; write-capable simplify passes on changed code; independent code review;
  root-cause investigation when Claude Code is stuck after one or two passes.
- **Keep in Claude Code:** planning, architectural review, cross-file synthesis, multi-source
  research, ticket structuring, strategy, conversation steering.
- **Fan-out workers:** resolve model names and effort levels from the current runtime, pin each
  worker to an explicit tier when the surface allows it, give every worker one owned result with a
  checkable completion criterion, and bound concurrency. Keep the reviewer independent from the
  implementer; a same-provider reviewer is a disclosed fallback.

## Mechanism

- Read-only review → `/codex:review --background` or `/codex:adversarial-review --background`.
- Write-capable rescue → `Agent(subagent_type: "codex:codex-rescue", prompt: "...")` with
  `run_in_background=true` **on the Agent tool itself**. Never pass `--background` inside the prompt
  and never pair it with `isolation: "worktree"`; both kill Codex early.
- **Runtime configuration is authoritative.** Read `~/.codex/config.toml` when the current model or
  effort matters; do not cache their values in agent documents.
- Do not run `/codex:setup --enable-review-gate`.

## Briefing

Brief it cold: paths, line numbers, success criteria, and the business intent the work serves.
Success criteria say when it is done; intent says which way to resolve the ambiguities they leave.
For read-only work say "review only, do not edit" explicitly; it defaults to `--write`. Never ask a
read-only job to run tests or `uv`: its sandbox denies all writes and the job thrashes on
`Operation not permitted`.

## Observability

Dispatch in the background and act on the completion notification. `status: running` is not
evidence of progress; more than ten consecutive minutes without new output or another progress
signal means the job is dead: cancel it, run `codex-hygiene` if needed, and report the failure
without retrying automatically.

`codex-hygiene` exits 1 and changes nothing while any job is still alive, so cancel first. If a job
is only stuck (status pinned to "running" after its process died, blocking new launches),
`codex-reconcile-phantoms.sh` clears it without killing anything.

## Adversarial review angles

Brief read-only with the diff or plan plus one angle:

**end-state alignment** · auth bypass · data loss · rollback safety · race conditions ·
degraded dependencies · version skew · observability gaps

End-state alignment is the mandatory first angle for a plan or spec; the other seven judge a plan on
its own framing. `/reverse-thinking` is the full method and is what to run inline when Codex is
unavailable.
