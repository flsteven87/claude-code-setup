---
description: Solo / main-based ship pipeline — simplify (Codex) → review (Codex) → commit & push to origin/main
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git stash:*), Task
disable-model-invocation: false
---

# /ship — End-to-end ship pipeline (main branch, no PR)

Drive a finalized change from working tree → committed → pushed to `origin/main`. All implementation review work is delegated to Codex per CLAUDE.md "Delegation to Codex" policy. This command is a thin orchestrator — each stage uses an existing skill or subagent.

## Stages

### 1. Pre-flight
- Run `git status --short` and `git diff --stat`.
- If working tree is clean AND no staged changes, abort with `Nothing to ship.`
- Show user a one-screen diff summary; confirm intent before proceeding.
- If user has unrelated staged changes mixed in, stop and ask whether to ship together or split.

### 2. Simplify (Codex)
Spawn `codex:codex-rescue` subagent with this brief:

> Run a simplify pass on the current working tree diff (`git diff HEAD`).
> Goals: drop duplication, improve naming, remove unused imports/branches,
> replace heavy patterns with simple ones, preserve behavior.
> Apply edits in place. Keep the public/behavioral surface unchanged.
> Report a one-line summary per file touched and any items where you
> intentionally did NOT simplify (with reason).

Wait for completion. The working tree now reflects Codex's edits.

### 3. Review (Codex)
Spawn a second `codex:codex-rescue` subagent with this brief:

> Independent code-quality review of the current working tree diff
> (`git diff HEAD`). Read CLAUDE.md, ~/.claude/rules/*.md, and any
> nearest project AGENTS.md. Surface findings as Important / Nit /
> Pre-existing with file:line. Comment-only — do NOT edit code.
> Cap Nits at 5; for more, say "plus N similar items" in summary.

Surface findings to the user with file:line references.

### 4. Decision gate (user)
Show:
- Final `git diff --stat`
- Simplify summary (stage 2)
- Review findings (stage 3)

Wait for user reply: `ship` / `abort` / `fix-first`.
- `fix-first` — loop back to stage 2 with the post-fix diff.
- `abort` — exit, working tree intact.
- `ship` — continue to stage 5.

### 5. Commit & push
- Auto-format hooks already ran during stage 2 edits (`auto-format.sh` PostToolUse).
- Draft a conventional commit message reflecting the change. Follow project commit-message style from recent `git log`. Do not add `Co-Authored-By` lines unless project CLAUDE.md specifies.
- `git add -A && git commit -m "<message>"`.
- `git push origin main`.
- Confirm push succeeded and report the new commit SHA.

## When NOT to use this command

- Implementation isn't done — use brainstorming → writing-plans → executing-plans first; `/ship` starts after code is written.
- PR-based work — use a feature branch + the `/code-review` plugin after pushing.
- Mixed worktree — uncommitted unrelated changes from other tasks should be split first.

## Failure modes

- Codex errors in stage 2/3 — stop, surface to user, do NOT auto-retry.
- Lint/type-check failures during commit — stop, show errors, user fixes then re-runs `/ship`.
- Push rejected (race) — stop, ask whether to `git pull --rebase` and retry.
