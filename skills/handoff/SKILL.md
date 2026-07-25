---
name: handoff
description: "Checkpoint the active repository into its root MEMORY.md so Codex or Claude Code can resume safely. Use when the user explicitly asks for a handoff, wrap-up, or end-of-session checkpoint."
argument-hint: "[next-session focus]"
disable-model-invocation: true
---

# Handoff

Replace the active repository's working checkpoint in `MEMORY.md`. The next session should be able
to resume without reading this conversation.

## Memory Contract

- Resolve the repository with `git rev-parse --show-toplevel`; the only persistence target is
  `<repo-root>/MEMORY.md`.
- Treat `MEMORY.md` as a compact operational cache. Git, pull requests, tickets, specs, plans, ADRs,
  and source files remain authoritative.
- Replace current state in place. Never append a dated session log or create a temporary handoff.
- Keep durable details in their owning artifacts and link to them. `CONTEXT.md` is Matt's
  ubiquitous-language glossary, not a WIP or session-state file.
- Preserve existing durable sections and user-owned decisions outside the checkpoint.

## Workflow

1. Read applicable `AGENTS.md` and `CLAUDE.md`, then inspect the existing `MEMORY.md` if present.
2. Ground the checkpoint with the smallest useful evidence:
   - `git status --short --branch`
   - `git rev-parse HEAD`
   - `git log --oneline -5`
   - referenced plans, tickets, pull requests, or validation results that affect the next action
3. Identify one primary objective, the verified current state, one exact next action, any active
   blocker or pending user decision, and the strongest durable pointers. Use invocation arguments
   to focus the next session.
4. Replace `## Current State` in `MEMORY.md`. If the file or section does not exist, create this
   minimal shape:

```markdown
# Project Memory

## Current State

- Objective: <one primary outcome>
- State: <verified progress and remaining boundary>
- Next: <one concrete action>
- Blocker: <blocker or "None">
- Anchor: `<branch>` at `<short-sha>`; worktree before checkpoint: <clean or concise dirty summary>

## Durable Pointers

- `<path-or-url>` — <why the next session may need it>
```

5. Keep only pointers that influence the next decision. Omit completed-work inventories, touched-file
   lists, speculative reasoning, and facts recoverable immediately from Git.
6. Inspect the final diff. Every state claim must be verified or explicitly marked unverified, and
   the file must contain no credentials, tokens, or personal data unnecessary for the work.

If the active directory is not inside a Git repository, return the checkpoint in chat and report
that no file was written. Do not choose another repository by recency or filesystem search.

## Completion

The handoff is complete when `MEMORY.md` names the objective, current state, exact next action,
blocker or decision status, Git anchor, and relevant durable pointers without duplicating their
content. Reply in the user's language with the exact file path and the next action in two or three
sentences.
