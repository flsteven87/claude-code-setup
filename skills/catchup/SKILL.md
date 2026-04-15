---
name: catchup
description: Use when the user says /catchup, wants to rebuild context after a reset, or needs a fast evidence-based summary of the current work before continuing.
---

# Catchup

Rebuild working context quickly from repository evidence instead of guessing.

## Workflow

1. Check the current branch, git status, changed files, and recent commits.
2. If a project memory file exists, read the active-work or next-steps section first.
3. Read only the highest-signal changed files or nearby plan docs.
4. Infer the active workstream, completed work, open questions, and next action.
5. State uncertainty explicitly if the evidence is weak.

## Output

Reply briefly in Traditional Chinese unless the user asked otherwise:
- Current task or likely workstream
- Key files or artifacts
- What appears done vs. in progress
- Recommended next step

## Rules

- Prefer git evidence and local memory files over narrative guesswork.
- Do not edit anything unless the user asks for changes.
- Keep the summary short enough that the user can resume immediately.
