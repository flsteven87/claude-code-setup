# Autonomous Loops Reference

> Moved out of CLAUDE.md 2026-07-25. Read this before starting any unattended / batch agent run.
> Evidence and dates: `~/Desktop/loop-engineering-research-2026-07-07.md`.

## Which tool

- **Batch grind work → `/ralph-loop`** (official plugin, installed 2026-07-07). Fits tasks with clear
  success criteria + automatic verification (tests / lint / typecheck): coverage backfill, mechanical
  migrations, lint sweeps. **NOT** for judgment or design work, vague specs, or production debugging.
- **Machine-off recurring work → `/schedule`** (cloud routine). `/loop` dies with the machine —
  it is in-session polling only.

## Operating rules

- **`--max-iterations` is mandatory.** The default is unlimited, and `--completion-promise` is
  exact-string matching, so it cannot express SUCCESS vs BLOCKED. Typical range 25–100.
- **Park, don't spin.** Three failed attempts on the same item → log it to a pending-for-human file
  and move on. Agent self-reports of "fixed" are not evidence (documented case: 20 consecutive false
  "fixed" claims on one error).
- **Externalize state.** Progress/status file + one commit per iteration. Files and git history are
  the loop's memory; context is disposable.
- **Staged adoption.** Run attended (human-in-the-loop) until the prompt is trusted, only then AFK.
  Overnight runs must fit inside the Max-plan session-limit window.
