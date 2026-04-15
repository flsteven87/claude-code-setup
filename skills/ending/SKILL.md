---
name: ending
description: Use when implementation is done and you need the full back-half pipeline — regression review → simplification → tidy commit → handoff. Triggers on '/ending', 'wrap this up', 'ship the changes', '收尾', '結束這個'.
---

# Ending — Back-Half Pipeline

Runs 4 skills in sequence to take finished code from "works" to "shipped + documented".

```
review-change → simplify → review-and-commit → handoff
  (regression)   (reduce)    (tidy+commit)      (memory)
```

## Mode Flag

Parse `$ARGUMENTS` for `--auto`:

- **Default (careful):** stop after each phase with a 1-line summary, wait for user "go"
- **`--auto`:** proceed automatically IF each phase reports CLEAN. If any phase flags issues → stop and ask, even under `--auto`

## Phase 1 — Review Change (regression + best-practice scan)

Invoke `Skill review-change`.

Expected output: findings list categorized (🔴 blockers / 🟡 suggestions / 🟢 nits).

**Gate:**
- 🔴 blocker present → STOP. Report. Ask user whether to fix now (loops back into `superpowers:executing-plans`) or defer
- Only 🟡/🟢 → proceed in both modes, carrying findings into Phase 2

## Phase 2 — Simplify (reduce complexity)

Invoke `Skill simplify`. Focus on the diff from Phase 1, plus any 🟡/🟢 findings.

**Gate:**
- Careful: show before/after summary, wait
- `--auto`: proceed if simplify only removes code or consolidates duplicates. If it introduces new abstractions → stop and confirm

## Phase 3 — Review and Commit (tidy + commit)

Invoke `Skill review-and-commit`. This phase:
- Cleans debug residue on changed files only
- Runs project lint / type-check
- Makes a conventional commit
- Pushes if on `main`

**Gate:** Commit is not a gate — once lint passes, commit. If lint fails, stop and report.

## Phase 4 — Handoff (memory)

Invoke `Skill handoff`. Updates MEMORY.md `## Active Work`, records new gotchas, marks completed items.

**Gate:** None — handoff is terminal.

## Completion

Print:
```
ending complete — commit <hash> on <branch>
```

## Rules

- Never skip Phase 1 — regression detection is load-bearing
- If review-change finds a regression that re-opens scope → loop back to `Skill superpowers:executing-plans` for the fix, then restart ending from Phase 1
- Do NOT commit with 🔴 blockers outstanding, even under `--auto`
