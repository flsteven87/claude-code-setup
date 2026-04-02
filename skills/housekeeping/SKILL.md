---
name: housekeeping
description: "Clean up and organize Claude Code artifacts: auto memory, CLAUDE.md, rules, completed plans, and stale docs. Use when the user says 'housekeeping', 'clean up', 'tidy', '整理', '清理', 'context hygiene', or at the start of a new project phase to reset accumulated cruft."
---
# Housekeeping

Perform a full audit and cleanup of Claude Code working artifacts. Goal: keep context lean, memory fresh, and docs current.

## Phase 1: Scan (always run first)

Execute the scan script to get a status report:

```bash
bash ~/.claude/skills/housekeeping/scripts/scan.sh
```

For a specific project only:
```bash
bash ~/.claude/skills/housekeeping/scripts/scan.sh --project /path/to/project
```

Present the scan results to the user. Do NOT delete or modify anything without explicit approval.

## Phase 2: Triage

After presenting scan results, organize findings into action categories and present them to user for approval:

### Category A: Safe to delete (low risk)
- Completed plan files (all items checked, no pending TODOs)
- Auto memory files older than 60 days with no recent references
- Duplicate or superseded memory files within the same project
- Empty or near-empty files (<5 lines with no meaningful content)
- Memory entries for completed features or obsolete decisions (derivable from code/git)
- File location pointers that are obvious from project structure

### Category B: Consolidate (medium risk)
- Multiple memory files in one project that overlap in topic → merge into one
- CLAUDE.md sections that should be rules files → extract to `~/.claude/rules/`
- Oversized memory files (>100 lines) → summarize key insights, trim verbose history

### Category C: Review with user (higher risk)
- Memory files that may still be relevant but are stale
- Rules that may be outdated due to project evolution
- CLAUDE.md content that may conflict with current project state

## Phase 3: Execute (only after user approval)

For each approved action:

### 3a. Clean completed plans
1. Verify the plan has no pending items (search for `[ ]`, `TODO`, `PENDING`, `IN PROGRESS`)
2. If all tasks are done, delete the plan file
3. If partially done, ask user whether to archive remaining items or delete entirely

### 3b. Tidy auto memory
Memory files live in `~/.claude/projects/<project-encoded>/memory/`.

**Core principle: only keep what helps future conversations.** If information can be derived from code, git history, or existing docs, it does not belong in memory. Aggressively trim — lean memory is better than comprehensive memory.

1. **Remove stale files**: Delete memory files approved for removal
2. **Consolidate overlapping files**: When multiple files cover the same topic:
   - Read all files
   - Merge unique insights into one file, using concise bullet points
   - Delete the source files after successful merge
   - Keep the most descriptive filename
3. **Trim oversized files**: For files >100 lines:
   - Extract key decisions, patterns, and constraints
   - Remove verbose history, step-by-step logs, and redundant explanations
   - Target <80 lines per file, <200 lines total per project
4. **Prune completed/obsolete entries**: Remove backlog items that are done, architecture notes for completed features, and file location pointers that are obvious from project structure

### 3c. Update CLAUDE.md
Check if global `~/.claude/CLAUDE.md` needs updates:

1. **Size check**: If >200 lines, identify sections that should move to `~/.claude/rules/`
2. **Freshness check**: Read current CLAUDE.md and compare against actual project patterns
3. **Conflict check**: Ensure no contradictions between CLAUDE.md and rules files
4. Extract topic-specific sections (>20 lines on one topic) into dedicated rule files

### 3d. Clean project-level docs
For each active project:

1. Remove orphan plan files (completed or abandoned)
2. Check for stale TODO files, scratch notes, or temp docs
3. Ensure `.claude/CLAUDE.md` (project-level) is up to date if it exists

## Phase 4: Report

After all actions complete, present a summary:

```
Housekeeping Complete
─────────────────────
Deleted:      X files (Y KB freed)
Consolidated: X memory files → Y files
Trimmed:      X files (Z lines removed)
Extracted:    X sections → rules files
Skipped:      X items (user declined)
```

## Safety rules

- **NEVER delete without explicit user approval** for each category
- **NEVER modify project source code** — only Claude Code artifacts (memory, plans, CLAUDE.md, rules)
- **Always show before/after** when consolidating or trimming files
- **Create backup** of any file before destructive edits: copy to `<filename>.bak` in the same directory
- If unsure whether something is still relevant, ask the user
