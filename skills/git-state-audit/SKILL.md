---
name: git-state-audit
description: Use when the user wants a full picture of a git repo's state across local and remote — status, branches, stash, worktrees, dangling/unpushed commits — followed by deep analysis and categorized cleanup recommendations. Triggers on 'audit git', 'git 全景', '整理 git', 'branch/stash/worktree 清理', 'git 現況', or before major cleanup/handoff.
---

# Git State Audit

Produce an evidence-based, full-picture audit of a git repository's local and remote state, then propose handling grouped by reversibility. **Report only — never execute destructive operations without explicit user confirmation.**

## Scope Discipline

- ✅ Read-only commands + `git fetch --prune` (safe, idempotent)
- ❌ No `git branch -D`, `stash drop`, `worktree remove`, `reset --hard`, `push --force`, `gc --prune` without user approval
- ❌ Do not touch files or commits outside audit scope

## Workflow

### 1. Collect (parallel where possible)

Run and capture — do NOT interpret yet:

```bash
git fetch --all --prune --tags 2>&1
git status -sb
git status -uall --porcelain        # untracked detail
git branch -vv                       # local + upstream tracking + ahead/behind
git branch -r                        # remote branches
git remote -v
git stash list --date=iso
git worktree list --porcelain
git log --oneline --all --graph --decorate -30
git reflog --date=iso | head -40
git for-each-ref --format='%(refname:short) %(upstream:track) %(committerdate:iso)' refs/heads
```

Dangling / unreachable commits (informational):
```bash
git fsck --no-reflogs --lost-found 2>&1 | head -20
```

### 2. Analyze — across five dimensions

| Dimension | Check for |
|---|---|
| **Working tree** | Staged vs unstaged, untracked (config? build artifact? in-progress?), line-ending / mode noise |
| **Branches** | Merged into default (safe delete), ahead-only (unpushed work), behind-only (stale), diverged (rebase/merge needed), no upstream (local-only), gone upstream (remote deleted) |
| **Stash** | Age (>30 days = likely stale), reference to branch that still exists, diff size |
| **Worktrees** | Orphan (branch merged/deleted), prunable, locked, path missing |
| **Remote sync** | Force-push risk (diverged shared branches), unpushed local tags, stale remote tracking refs |

### 3. Report — structured output

Reply in Traditional Chinese unless user requested otherwise.

```
## Git 全景
- Repo / 當前 branch / HEAD
- Working tree: <clean | N staged, M unstaged, K untracked>
- Branches: <local count> local (<ahead> ahead, <behind> behind, <gone> gone), <remote count> remote
- Stash: <count> entries (oldest: <age>)
- Worktrees: <count> (<orphan> orphan)

## 深度分析
[Grouped findings with evidence — cite the git command output]

## 處置建議（依風險分級）

### 🟢 Safe（可逕行執行，可還原）
- `git fetch --prune` — 清除已刪除的 remote tracking refs
- …

### 🟡 Needs Review（需使用者確認語義）
- `git branch -d feature/foo` — 已合併進 main（若非 main merge 則改用 -D，請確認）
- Stash@{3}（建立於 2026-01-02，引用 branch `bar` 已不存在）→ 確認是否保留

### 🔴 Destructive（破壞性，需明確授權）
- `git worktree remove ../old-wt --force` — 內有未提交變更
- Force-push `feature/x`（已與 origin 分歧 N commits）
- `git reflog expire` / `git gc --prune=now`
```

### 4. Ask before acting

Never run anything in 🟡 or 🔴 without explicit user approval for that specific item. Batching destructive operations is not approval.

## Edge Cases

- **Detached HEAD** → Flag prominently; list commits reachable only from HEAD before any branch switch suggestion
- **Submodules** → Check `git submodule status`; report dirty / detached submodules
- **LFS** → Note if `.gitattributes` has LFS filters but `git lfs status` shows mismatches
- **Shallow clone** → `git rev-parse --is-shallow-repository`; warn that branch/commit analysis may be incomplete
- **No remote configured** → Skip remote-sync dimension, note explicitly

## Red Flags — STOP and escalate

- Uncommitted changes in a worktree slated for removal
- Stash referencing a detached commit with no branch
- Local branch ahead of origin AND origin force-pushed (lost commits risk)
- Dangling commits newer than 7 days in fsck output (possibly dropped work)

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running `fetch --prune` without `--tags` then reporting "no tags to prune" | Always include `--tags` |
| Treating `[gone]` branches as safe-delete without checking ahead count | `[gone]` + ahead > 0 = unpushed work, needs review |
| Counting untracked files without classifying | Split untracked into: ignored-worthy, in-progress, build artifact |
| Suggesting `branch -d` for branches merged via squash/rebase | Squash-merged branches need `-D` with explicit confirm — explain why |
| Auto-pruning worktrees without `list --porcelain` inspection | Locked or in-use worktrees fail silently; inspect first |

## Output Principle

**Evidence first, recommendation second.** Every recommendation must cite which command output justifies it, so the user can verify without re-running.
