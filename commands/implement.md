---
description: Plan-driven implementation with size-aware triage — Codex executes, CC orchestrates, Karpathy-style surgical scope. Does NOT commit; chain /ship when ready.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git ls-files:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm run:*), Bash(npm test:*), Bash(cargo:*), Bash(go vet:*), Bash(go test:*), Bash(test -f:*), Bash(ls:*), Read, Skill, Task
disable-model-invocation: false
---

# /implement — Plan-driven implementation with smart triage

Drive a planned change from spec → working code. CC triages scope and orchestrates; Codex does the heavy lifting per CLAUDE.md "plan here, ship there". This command does NOT commit or push — chain `/ship` (or pass `--then-ship`) when ready.

## Flags

- `--then-ship` — on clean completion, automatically invoke `/ship`. Default: stop and report.
- `--light` / `--heavy` — override the triage verdict.

## Inputs (no positional args)

Read from, in this order:
1. **Conversation context** — preceding discussion / plan content / file refs
2. **`MEMORY.md ## Active Work`** — nearest active 🔴 item, as fallback
3. **Any plan file referenced recently** — read it

If none yields a clear, bounded task → STOP and ask user (suggest `/writing-plans` first).

---

## Stage 0: Triage (CC, follows karpathy-guidelines)

1. **Load principles**: invoke `Skill karpathy-guidelines` — applies throughout.
2. **Resolve task source** per the input order above.
3. **Define verifiable success criteria** for each task — concrete check (test cmd, file state, observable behavior). No fuzzy "looks good".
4. **Surface assumptions** — list any ambiguous decisions. High-stakes → ask user before continuing.
5. **Pick mode** — ANY of these triggers `heavy`:
   - Plan has ≥ 3 explicit tasks/checkpoints
   - Touches ≥ 5 files (estimate from plan/context)
   - Crosses layers (schema + service + API + frontend etc.)
   - Touches migration / auth / RLS / payments / billing
   - `--heavy` flag passed
   - Default = `light`. User can force with `--light`.
6. **Print verdict** (one block) and wait for `go` / questions:
   ```
   mode:        light | heavy
   reason:      <one line>
   tasks:       - task 1 [success: <criterion>]
                - task 2 [success: <criterion>]
   assumptions: <any surfaced; "none" if clean>
   ```

---

## Stage 1A: Light mode (single-shot)

Spawn ONE `codex:codex-rescue` with this brief:

> **Task**: <consolidated task statement>
> **Success criteria**: <verifiable checks>
> **Karpathy rules**:
> - Surgical scope only — do not refactor adjacent code or rename unrelated symbols
> - Surface assumptions instead of silently deciding ambiguous cases
> - No defensive branches for impossible states
> - No premature abstraction; three similar lines beat a half-baked helper
> **Out of scope**: <explicit no-go list>
> Apply edits in place. Report one-line summary per file touched + any item you intentionally did NOT change (with reason).

After Codex returns:
- Run verify gate (same manifest detection as `/ship` stage 3).
- Fail → ONE Codex retry with the failing output. Still failing → stop, surface to user.

---

## Stage 1B: Heavy mode (per-task with CC checkpoints)

For each task in plan order:

1. **Brief Codex** — one `codex:codex-rescue` per task:
   > **Task N of M**: <THIS task only>
   > **Success criterion**: <verifiable check for THIS task>
   > **Karpathy rules**: surgical scope, surface assumptions, no defensive branches, no premature abstraction
   > **Out of scope**: any file or area not listed in this task — including future tasks in the plan
   > Report files touched and any deviation.

2. **CC Checkpoint (do not skip)**:
   - Run task's success criterion command(s).
   - `git diff HEAD` since last checkpoint → confirm changes stay within the task's declared scope.
   - Pass → next task.
   - Scope creep → stop, surface offending file:line.
   - Success criterion fail → ONE Codex retry with the failing output. Still failing → stop.

3. **Stop conditions**: Codex reports cannot proceed, two consecutive checkpoint failures on same task, or user interrupts.

---

## Stage 2: Final report (must fit one screen)

```
implement complete — <mode>
tasks:    <N done> / <M total>
files:    <count> changed
verify:   <pass | pass-after-retry | skipped: no-gate>
karpathy: <clean | N items surfaced>
next:     /ship    (or rerun with --then-ship)
```

Followed by a max-10-line bullet list of what changed + any open assumption.

If `--then-ship` AND all stages clean → invoke `/ship`. Otherwise stop here.

---

## When NOT to use

- No discussion / plan in context AND `MEMORY.md ## Active Work` empty → run `/writing-plans` first.
- Mid-debugging — use `systematic-debugging` skill, then `/ship`.
- Working tree already has the implementation done → straight to `/ship`.

## Failure modes

- Triage cannot resolve a clear task → stop, ask user.
- Codex fails to apply edits → stop, surface output. No auto-retry beyond the one allowed per stage.
- Verify gate fails twice → stop, hand back to user with failing command + diff.
- Scope creep at heavy checkpoint → stop, do NOT auto-revert; user decides.
