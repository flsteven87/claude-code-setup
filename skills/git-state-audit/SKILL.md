---
name: git-state-audit
description: Use when the user wants their git repo brought to a known-clean, remote-synced state — covers full local+remote audit (status, branches, stash, worktrees, dangling commits), rebase, conflict resolution, merged-branch/worktree cleanup, and verification. Default mode runs the safe cleanups end-to-end (not just reports). Triggers on 'audit git', '整理 git', '清乾淨', 'git 全景', 'git 現況', 'rebase 一下', 'branch/worktree 清理', or before major handoff. Run report-only if the user explicitly says 'just audit' / '只看不要動'.
---

# Git State Audit & Cleanup

Bring a git repo to a known-clean, remote-synced state — and prove it. Audit first, then execute the cleanups whose semantics are unambiguous; stop and ask the human only when the next step is genuinely destructive or judgment-laden.

The skill replaces "report and wait for permission on every line" with "do the obvious stuff, surface what actually needs a human."

## Mode

| Mode | When | Behavior |
|---|---|---|
| **Audit + Cleanup** (default) | Default for trigger phrases above | Run all 🟢 actions automatically. Ask once per 🟡 cluster. Never run 🔴 without an explicit per-item OK. |
| **Audit only** | User says "just audit / 只看 / report only / 先別動" | Skip all execution. Output report only. |

If unsure which mode the user intends, default to Audit + Cleanup but state the assumption in the opening line so they can redirect.

## Scope Discipline

- ✅ Read-only commands + `git fetch --all --prune --tags` (idempotent)
- ✅ Cleanups whose preconditions are deterministically checkable from git itself: `worktree remove` (clean tree), `branch -d` (merged), `rebase` against a clean branch, `rmdir` empty CC scaffolding dirs
- ❌ Never without explicit per-item OK: `branch -D`, `stash drop`, `reset --hard`, `push --force`, `worktree remove --force`, `gc --prune=now`, `reflog expire`, discarding uncommitted working-tree changes, `gh auth switch` (touches global state)
- ❌ Do not touch files or commits outside the audit scope (no opportunistic refactors / commits / format passes)

## Workflow

### Phase 1 — Collect (read-only, parallel)

Run these in one batch and capture raw output — do not interpret yet:

```bash
git fetch --all --prune --tags 2>&1
git status -sb
git status -uall --porcelain
git branch -vv
git branch -r
git remote -v
git stash list --date=iso
git worktree list --porcelain
git log --oneline --all --graph --decorate -30
git reflog --date=iso | head -40
git for-each-ref --format='%(refname:short) %(upstream:track) %(committerdate:iso)' refs/heads
git fsck --no-reflogs --lost-found 2>&1 | head -20
```

If `git fetch` fails with `Repository not found` / `403`, it's almost always a **multi-account `gh` / credential-helper mismatch**, not a network problem. Diagnose with `gh auth status` and surface the switch command (e.g. `gh auth switch --user <org-user>`) — but **don't run it yourself** without explicit OK; it mutates the user's global gh state. Continue the audit with stale remote-tracking data and flag it.

### Phase 2 — Analyze (five dimensions)

| Dimension | Check |
|---|---|
| **Working tree** | Staged/unstaged/untracked. **Untracked classification matters**: in-progress (subset of branch name scope?) / build artifact (should be `.gitignore`'d) / tooling scaffolding (e.g. `.claude/worktrees/`) / mystery |
| **Branches** | Merged into default (FF or squash) / ahead-only / behind-only / diverged / no upstream / `[gone]` upstream / orphan (no commits past base) |
| **Stash** | Age, referenced branch still exists, scope |
| **Worktrees** | Orphan (branch merged/deleted), checked-out branch, clean? locked? path missing? |
| **Remote sync** | Force-push risk on diverged shared branches, unpushed tags, stale remote-tracking refs |

**Squash-merge detection** is non-obvious — `git branch --merged main` misses squash-merged branches. Cross-check with `git cherry main <branch>`: all lines starting with `-` means every commit's patch is already in main (likely squash-merged). Branch is still safe to delete, but `git branch -d` will refuse; needs `-D` which is 🔴.

**Branch–HEAD ancestry** for worktree branches: a worktree branch whose tip is an ancestor of `origin/main` (`git merge-base --is-ancestor <branch> origin/main`) is fast-forward-merged and safe to delete after the worktree is removed.

### Phase 3 — Triage

Classify every finding into one of three buckets. The bucket determines what happens in Phase 4.

#### 🟢 Auto-execute (run without asking)

Preconditions are checkable from git output, action is reversible or git-recoverable, no working-tree mutation:

- `git fetch --all --prune --tags` (already done in Phase 1)
- Pruning stale remote-tracking refs (covered by `--prune`)
- `git worktree prune` for worktrees whose path is missing
- `git worktree remove <path>` when the worktree's tree is clean AND its branch tip is ancestor of `origin/main` (i.e. merged)
- `git branch -d <name>` for branches that `git branch --merged <default>` lists (FF/merge-commit merged, no commits at risk)
- `rmdir <parent>` for empty directories left behind after worktree removal (e.g. `.claude/worktrees/` when empty)
- `git rebase origin/<base>` for a branch that has unpushed commits AND is cleanly fast-forwardable / no conflicts

#### 🟡 Confirm-then-execute (ask once with a clear yes/no)

Action has a deterministic outcome but the human still owns the call:

- Uncommitted working-tree changes (see WIP Triage below) → commit / stash / discard / pause
- `git branch -d` on squash-merged branches (needs `-D`, but the cherry check shows it's safe)
- Rebase that produces conflicts → propose per-file resolution, then confirm before `--continue`
- Stash entries >30 days old referencing branches that still exist → keep or drop
- `gh auth switch --user <name>` to unblock fetch

#### 🔴 Stop (per-item explicit OK only — no batching)

Genuinely lossy or remote-visible:

- `git branch -D` on a branch with unpushed commits
- `git worktree remove --force` on a dirty worktree
- `git reset --hard`, `git restore` on files the user touched, `git clean -fd`
- `git push --force` / `--force-with-lease`
- `git gc --prune=now`, `git reflog expire`
- Discarding any uncommitted change the human didn't pre-authorize

### Phase 4 — Execute

Order matters. State can shift between commands (parallel CC sessions, IDE saves, watch processes) — **re-verify the precondition immediately before each destructive op**. This skill has been burned by a `git status` going from "dirty with 4 files" to "clean" between two checks within seconds; that's not paranoia, that's the actual ground state.

1. **WIP triage first.** If `git status` is non-clean, resolve it before anything else (you can't claim "clean state" otherwise, and rebase will refuse).
2. **Rebase next.** Branches that need to catch up. Conflict handling: see below.
3. **Worktrees before branches.** `git branch -d` refuses if branch is checked out anywhere. Always `git worktree remove` first.
4. **Empty parent rmdir.** After removing the last worktree under a parent (e.g. `.claude/worktrees/`), the parent dir is left behind and shows up as untracked. `rmdir` it.
5. **Re-fetch + re-audit.** Run the Phase 1 batch again (lighter — just `status / branch -vv / worktree list / stash list`) to prove clean.

#### WIP Triage Pattern

If the working tree has uncommitted changes, do NOT proceed silently. Classify:

| Signal | Interpretation | Default offer |
|---|---|---|
| Diff scope matches current branch name (e.g. branch `remove-foo`, diff deletes `foo/`) | In-progress feature work | **A. Commit + push** / **B. Stash** / **C. Discard** / **D. Pause cleanup** |
| Diff is on `main` or unrelated to branch name | Accidental — possibly another session's work, or stale editor save | Pause, surface the diff, let user identify |
| Untracked is `.claude/worktrees/<name>/` | CC sub-agent scaffolding | Treat as part of worktree dimension, not WIP |
| Untracked is build artifact (`__pycache__`, `dist/`, `.venv/`) | `.gitignore` gap | Offer to add the rule (separate commit) |

Present as a small table with A/B/C/D, not as a wall of prose. Wait for the letter. **Never `git restore` / `git clean` / `git checkout -- .` to "make status clean" without explicit C from the user** — that's data loss disguised as cleanup.

#### Rebase + Conflict Workflow

1. `git rebase origin/<base>` (or whichever base the user implied — usually `main`).
2. If it succeeds: log it and move on.
3. If conflicts:
   - `git diff --name-only --diff-filter=U` to list conflicted files
   - For each: read the file, identify both sides, **propose a specific resolution** with reasoning ("on file X, lines A–B keep ours because Y; on lines C–D take theirs because Z")
   - Ask for OK on the proposal
   - On OK: write the resolved file, `git add`, `git rebase --continue`
   - On NO or unclear: `git rebase --abort` to return to clean pre-rebase state, hand back to user
4. **Never** use `-X ours` / `-X theirs` blindly — they apply globally and silently drop entire hunks. Per-file resolution with reasoning is the floor.

#### gh / Credential Mismatch Pattern

If `git fetch` failed in Phase 1:

```
gh auth status                          # shows active account
gh auth status | grep -i 'active\|user' # confirm mismatch
```

If a different `gh` user has access (memory or `~/.claude/CLAUDE.md` may name the correct one for this repo), propose:

```
gh auth switch --user <correct-user>
```

This is 🟡 — ask once, run after explicit OK. After switch, re-run `git fetch` to verify.

### Phase 5 — Verify

After execution, prove the end state. Re-run:

```bash
git status -sb
git branch -vv
git worktree list
git stash list
git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads
```

The "clean" claim requires all of:

- `git status -sb` shows only the branch header line (no `M`/`D`/`A`/`??`)
- Every local branch either has upstream and is `[gone]`-free, ahead/behind both zero, OR is explicitly known-local-only and noted
- `git worktree list` matches what you expect (no orphans)
- `git stash list` empty OR every entry justified
- `git fsck` dangling count didn't grow (existing dangling from old amends/aborts is fine — `git gc` will eat them)

If any of these fails, don't claim clean. Report what's left and why.

### Phase 6 — Report

Reply in Traditional Chinese unless user requested otherwise. Template:

```
## Git 全景
- Repo / 當前 branch / HEAD
- Working tree: clean | N staged, M unstaged, K untracked  ← end-state
- Branches: <n> local, <m> remote, all in sync (or list deltas)
- Stash: <n> entries (oldest age)
- Worktrees: <n>

## 執行了
- ✅ <action> — <one-line evidence>
- ✅ <action> — <one-line evidence>

## 待你決定（若有）
- 🟡 <item> — A / B / C 選項
- 🔴 <item> — 需要明確 OK

## 注意（informational, no action needed）
- <e.g. dangling 物件 N 個，2026-05-10 amend 殘留，會被 git gc 自動清>
```

If `Mode = Audit only`, swap the "執行了" section for the original "處置建議（依風險分級）" 🟢/🟡/🔴 list.

## Edge Cases

- **Detached HEAD** → Flag prominently; before any branch switch, list commits reachable only from HEAD to confirm none are orphaned by the switch.
- **Submodules** → `git submodule status`; dirty/detached submodules are out of scope for auto-execute, surface to user.
- **LFS** → If `.gitattributes` has LFS filters, run `git lfs status` and note mismatches; don't auto-fetch/push LFS objects.
- **Shallow clone** → `git rev-parse --is-shallow-repository`; if true, branch/commit analysis is incomplete, warn and limit claims.
- **No remote configured** → Skip remote-sync dimension entirely, note explicitly. All branches are local-only by definition.
- **`.claude/worktrees/`** (Claude Code scaffolding) → CC's `/ship` stage 7 normally sweeps these. If you find an orphan one whose branch is merged, it's safe to clean via the standard worktree-remove path. If branch is unmerged, treat as a sub-agent's in-progress work and leave alone unless user confirms.

## Red Flags — STOP

- Uncommitted changes in a worktree slated for removal — stop, do not `--force`
- Stash referencing a commit not on any branch (detached) — losing this stash loses the only ref
- Local branch ahead of origin AND origin force-pushed since last fetch (`git reflog show origin/<branch>` shows non-FF) — possible lost commits, do not rebase blindly
- Dangling commits newer than 7 days in `fsck --lost-found` — possibly dropped work, surface SHAs before any gc
- `git status` output changes between two checks within the audit — another process is writing the tree; pause and tell user

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running `fetch --prune` without `--tags` | Always include `--tags` — stale tags are a real source of confusion |
| Treating `[gone]` branches as safe-delete without checking ahead count | `[gone]` + ahead > 0 = unpushed work that just lost its remote; needs review, not auto-delete |
| Counting untracked without classifying | Always classify: WIP / build artifact / gitignore gap / tooling scaffolding |
| Suggesting `branch -d` for squash-merged branches | `-d` refuses; cross-check with `git cherry`, then it's 🟡 `-D` with the evidence in hand |
| Pruning worktrees without `list --porcelain` inspection | Locked / in-use worktrees fail silently; always inspect first |
| Branch delete before worktree remove | `branch -d` refuses if checked out anywhere; worktree first, always |
| Trusting Phase 1 snapshot when running Phase 4 minutes later | Parallel sessions / IDE saves shift state; re-verify preconditions immediately before each destructive op |
| Using `-X ours` / `-X theirs` to "auto-resolve" conflicts | Drops entire hunks silently; do per-file with reasoning or abort |
| Running `gh auth switch` to "fix" fetch without asking | Mutates global gh state, can stash the wrong user mid-flow elsewhere; always 🟡 |
| Claiming "clean state" without re-running `git status` post-execution | Phase 5 verification is non-negotiable — actions can fail silently |
| `git restore` / `git clean` to make status clean | That's discarding the user's work. WIP triage with A/B/C/D first, always |

## Output Principle

**Evidence first, action second, claim third.** Every action must cite the git command output that justified it. Every "clean state" claim must cite a post-execution verification command, not Phase 1 data. The human should be able to verify any line of the report without re-running anything.
