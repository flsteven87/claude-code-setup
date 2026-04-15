---
name: handoff
description: Use when the user says /handoff or wants end-of-session continuity notes, pending work capture, and the cleanest next-session starting point.
---

# Handoff

Capture the minimum durable context needed to resume work safely in the next session.

## Workflow

1. Inspect current branch, git status, recent commits, and changed files.
2. Summarize completed work, pending work, key decisions, and next actions.
3. If the project has an established memory file, update it in place.
4. Otherwise, provide the handoff summary directly and ask before writing new persistent files.

## Preferred Memory Targets

Check in this order:
- `MEMORY.md`
- `.claude/MEMORY.md`
- project-specific handoff or memory conventions already present

## Output

Capture:
- Current status
- Completed work
- Pending tasks
- Key files
- Important decisions
- Recommended next step

## Rules

- Prefer one durable exchange point over scattering handoff files.
- Do not invent a project memory convention if one already exists.
- Keep the summary actionable, not narrative.
