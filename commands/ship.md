---
description: Solo / main-based ship pipeline — simplify (Codex) → review (Codex) → commit & push to origin/main
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git stash:*), Bash(git worktree:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm run:*), Bash(npm test:*), Bash(cargo:*), Bash(go vet:*), Bash(go test:*), Bash(test -f:*), Bash(ls:*), Task
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

### 3. Verify (auto, behavior-preserving gate)
Detect the repo's gate scripts from manifest presence and run the smallest relevant set. Stop on first failure.

- **Python (`uv.lock`)**: `uv run ruff check .` → `uv run pytest -x` (skip pytest if no `tests/` or `test_*.py`)
- **pnpm (`pnpm-lock.yaml`)**: existing `lint`, `typecheck`, `test` scripts (skip ones not defined)
- **npm (`package-lock.json`)**: existing `lint`, `typecheck`, `test` scripts
- **Cargo (`Cargo.toml`)**: `cargo clippy -- -D warnings` → `cargo test`
- **Go (`go.mod`)**: `go vet ./...` → `go test ./...`
- **No manifest match**: log `verify: no gate detected, skipping` and continue.

**On failure:**
- Spawn `codex:codex-rescue` with brief: failing command + last ~100 lines of stderr + "fix without changing public API surface or tests; preserve behavior."
- After Codex finishes, re-run the failing command **once**.
- Pass on retry → continue to stage 4.
- Fail on retry → STOP. Surface error + Codex diff to user. Do NOT auto-retry further.

### 4. Review (Codex)
Spawn a second `codex:codex-rescue` subagent with this brief:

> Independent code-quality review of the current working tree diff
> (`git diff HEAD`). Read CLAUDE.md, ~/.claude/rules/*.md, and any
> nearest project AGENTS.md. Surface findings as Important / Nit /
> Pre-existing with file:line. Comment-only — do NOT edit code.
> Cap Nits at 5; for more, say "plus N similar items" in summary.

Surface findings to the user with file:line references.

### 5. Decision gate (user)
Show:
- Final `git diff --stat`
- Simplify summary (stage 2)
- Verify result (stage 3) — passed cleanly / passed after Codex fix
- Review findings (stage 4)

Wait for user reply: `ship` / `abort` / `fix-first`.
- `fix-first` — loop back to stage 2 with the post-fix diff.
- `abort` — exit, working tree intact.
- `ship` — continue to stage 6.

### 6. Commit & push
- Auto-format hooks already ran during stage 2 edits (`auto-format.sh` PostToolUse).
- Draft a **Conventional Commit** message: prefix one of `feat|fix|chore|docs|refactor|test|perf`, colon, space, imperative subject under 70 chars, no period. Body optional, focus on *why* not *what*. Do not add `Co-Authored-By` unless project CLAUDE.md specifies.
- `git add -A && git commit -m "<message>"`.
- `git push origin main`.
- Confirm push succeeded and report the new commit SHA.

### 7. Worktree cleanup (post-push)
Stale worktrees under `.claude/worktrees/` break tooling that walks the repo (e.g. `shopify app dev` aborts on duplicate `shopify.web.toml`; same shape for any CLI that scans `**/package.json`, `**/*.toml`, etc.). Clean them as part of ship so they don't accumulate.

- Run `git worktree list`. For each worktree under `.claude/worktrees/`, check whether its branch is fully merged into `origin/main`: `git log origin/main..<branch>` is empty AND `git -C <path> status --short` is clean.
- Surface the candidates to the user (path + branch + last-commit SHA) and ask before removing. Include the **current** worktree if /ship ran from one and it now qualifies.
- On confirm, for each:
  - `git worktree remove <path>` (run from the main repo, not from inside the worktree being removed)
  - `git branch -d <branch>` — `-d` is safe; it refuses unmerged branches. Never use `-D`.
- Skip (do not prompt) any worktree that is dirty, has unpushed commits, or whose branch has commits not in `origin/main`.

## When NOT to use this command

- Implementation isn't done — use brainstorming → writing-plans → executing-plans first; `/ship` starts after code is written.
- PR-based work — use a feature branch + the `/code-review` plugin after pushing.
- Mixed worktree — uncommitted unrelated changes from other tasks should be split first.

## Failure modes

- Codex errors in stage 2/4 — stop, surface to user, do NOT auto-retry.
- Verify failure (stage 3) — one Codex rescue attempt; if retry still fails, stop and hand back to user.
- Push rejected (race) — stop, ask whether to `git pull --rebase` and retry.
