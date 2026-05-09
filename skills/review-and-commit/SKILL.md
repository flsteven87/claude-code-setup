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

## Graphify Update

Before staging and committing, refresh Graphify outputs when the repository has a Graphify workflow.

1. Check whether the repo defines Graphify commands:
   - Prefer `npm run graph:status` or `./scripts/graphify.sh status` when available.
   - If no Graphify workflow exists, skip this section and say it was not applicable.
2. Use `git diff --name-only` and `git diff --cached --name-only` to identify touched files.
3. Rebuild only affected surfaces when the repo uses surface graphs:
   - `backend/src/**` -> `./scripts/graphify.sh build backend/src`
   - `backend/tests/**` -> `./scripts/graphify.sh build backend/tests`
   - `frontend/**` -> `./scripts/graphify.sh build frontend`
   - `blog/**` -> `./scripts/graphify.sh build blog`
4. If changes span many surfaces or the repo does not have surface-specific commands, run the repo's documented all-graph command, such as `npm run graph:build:all`.
5. Run the graph status command after rebuilding.
6. Include updated tracked graph outputs, such as `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json`, in the commit. Do not stage Graphify cache, manifest, cost, transcript, or other ignored local internals.

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
