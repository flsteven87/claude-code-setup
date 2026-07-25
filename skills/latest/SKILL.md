---
name: latest
description: "Safely refresh the active default checkout and reconcile its root MEMORY.md with current Git, pull requests, tickets, changelog, and directly relevant repository evidence. Use when project memory has drifted or needs consolidation."
argument-hint: "[specific workstream or scope]"
disable-model-invocation: true
---

# Latest

Bring the active repository and its repo-root `MEMORY.md` up to verified reality so the user can
start the next piece of work.

## Boundaries

- `MEMORY.md` is a compact operational cache shared by Codex and Claude Code. Git, pull requests,
  tickets, specs, ADRs, changelog, and source files remain authoritative.
- Scope is the active repository plus sibling repositories explicitly named by the user or linked
  from memory because they affect the active objective.
- Preserve user-owned decisions and load-bearing constraints. Report contradictory evidence as a
  tension instead of silently rewriting them.
- `CONTEXT.md` remains a ubiquitous-language glossary. Use it to interpret domain terms, not to
  store current work or session history.
- Keep implementation, team-visible ticket mutations, commits, pushes, stashes, rebases, merges,
  deletions, and unrelated cleanup outside this workflow.

## Workflow

1. Resolve the repo root, current branch, upstream, and `<repo-root>/MEMORY.md`. Read applicable
   `AGENTS.md` and `CLAUDE.md`.
2. Read the memory before gathering external evidence. Extract only claims and pointers that affect
   the current objective.
3. Refresh repository truth:
   - fetch remote refs and tags when access is available;
   - inspect status, divergence, recent default-branch commits, tags, and the top of `CHANGELOG.md`;
   - verify only the pull requests and tickets named by the current checkpoint or user scope.
4. On `main`, `master`, or `trunk`, fast-forward with `git pull --ff-only` only when:
   - the branch has an upstream and is behind;
   - `git merge-base --is-ancestor HEAD @{u}` succeeds;
   - there are no tracked local changes; and
   - untracked files do not collide with incoming paths.
   Otherwise leave the checkout untouched and report the exact blocker. Feature branches and sibling
   repos are fetch-only unless the user explicitly requests more.
5. Classify memory content:
   - verified and still needed for the next decision;
   - stale with an unambiguous correction;
   - accurate but better represented by a short pointer;
   - user-owned tension;
   - unverified.
6. Reconcile the existing `MEMORY.md`:
   - replace `## Current State` with one objective, verified state, exact next action, blocker or
     pending decision, and current Git anchor;
   - keep only load-bearing constraints and pointers to durable artifacts;
   - correct stale mechanical facts and remove completed session narrative;
   - preserve tensions unchanged and name them in the report.
7. Inspect the final diff and verify every changed claim against the evidence used.

If repo-root `MEMORY.md` does not exist, do not create it during `latest`. Report `NO_MEMORY`, provide
the verified current state, and recommend `handoff` when the user wants to establish the shared
checkpoint.

## Memory Quality

Prefer a file under 120 lines, with details behind pointers. This is a focus target rather than
permission to discard required constraints. Never append dated session blocks or copy ticket,
pull-request, commit, and diff histories into memory.

## Completion

`latest` is complete when the default checkout was fast-forwarded, was already current, or was left
untouched with an exact safety reason; each memory edit has evidence; tensions remain visible; and
the next action is explicit.

Reply in the user's language with synced sources, checkout result, memory changes, tensions or
validation gaps, and a two-to-three-sentence ready-next summary.
