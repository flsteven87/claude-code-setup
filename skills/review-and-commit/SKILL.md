---
name: review-and-commit
description: Use when deep review is already done and you need a final tidy-up pass (remove debug artifacts, unused imports, dev comments) then commit with a conventional message. Triggers on '/review-and-commit', '收尾 commit', 'tidy and commit'.
---

# Review and Commit — Light Finishing Pass

> Assumes deep review already ran (e.g. via `review-change`). This skill is the **last mile** only.

## Scope Rule

1. Run `git diff --name-only` to get the touched files
2. **Only inspect and clean those files** — do not touch anything else
3. If you notice issues in other files → report them, do NOT fix silently

## Cleanup Checklist

Quick scan of changed files for debug residue:

- [ ] Remove `console.log`, `print()` debug statements
- [ ] Remove commented-out code blocks
- [ ] Remove `// TODO`, `// HACK`, `// FIXME` dev comments
- [ ] Remove unused imports and variables
- [ ] Verify no `.env`, credentials, or sensitive files are staged

If you find anything substantive (not just debug residue), stop and recommend a full `review-change` pass.

## Verify then Commit

```bash
# Project-appropriate checks — read CLAUDE.md for exact commands
cd backend && uv run ruff check .
cd frontend && npx tsc -b && pnpm lint
```

Then:

```bash
git add <touched files>
git commit -m "<conventional commit>"
```

- Conventional commit in concise English
- Do NOT mention AI, Claude, or Codex in the message

## Push Rule

- On `main` → `git push origin main`
- On feature branch → commit only; push only if user asks

## MEMORY.md Update

After commit, update project memory if the session produced lasting knowledge:

**Write:**
- New gotchas / traps
- Architecture or pattern changes
- New important paths or hooks
- Backlog state changes (completed → ✅, new items appended)

**Clean:**
- Fixed traps (no longer reachable)
- Completed backlog items
- Descriptions out of sync with current code

**Skip:**
- Transient session context (task detail, debug trace)
- Unverified speculation
- Rules already covered by CLAUDE.md

Keep MEMORY.md lean, accurate, in sync.
