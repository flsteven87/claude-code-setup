---
name: ship
description: Full end-to-end pipeline for a topic/issue/feature — composes /building (reverse-thinking → brainstorming → writing-plans → executing-plans) then /ending (review-change → simplify → review-and-commit → handoff). Triggers on '/ship', 'ship this', 'take it from idea to commit', '從頭到尾做完'.
---

# Ship — End-to-End Pipeline

Two-stage composition:

```
/ship = /building → /ending

/building → reverse-thinking → brainstorming → writing-plans → executing-plans
/ending   → review-change → simplify → review-and-commit → handoff
```

## Usage

```
/ship <topic or issue>
/ship <topic> --auto
```

- `$ARGUMENTS` first token is the topic; `--auto` flag flows through to both sub-skills
- No topic → read MEMORY.md `## Active Work` for the top 🔴 item; confirm with user before starting

## Execution

1. Invoke `Skill building` with the topic + flags
2. On `building complete` → invoke `Skill ending` with the same flags
3. On `ending complete` → print final summary:
   ```
   ship complete
   topic: <topic>
   commits: <sha1>..<shaN>
   MEMORY.md updated: yes
   ```

## Mode Flag Propagation

- `/ship --auto` → both `/building --auto` and `/ending --auto`
- Each sub-skill independently decides when to degrade to careful mode per its own rules
- `reverse-thinking` (inside /building) is the **master gate**: if it flags HIGH risk, `--auto` is disabled for the rest of the pipeline

## Bailout Rules

- `/building` fails → stop, do NOT auto-start `/ending`. Report which phase broke
- `/ending` finds 🔴 blocker → loop back into `Skill superpowers:executing-plans` for fix, then restart `/ending` from Phase 1 (not the whole `/ship`)
- User interrupts mid-flow → save current phase state in your reply so resume is trivial

## Why Two Sub-Skills

- Composability: run only `/building` when handing off code to someone else to finish; run only `/ending` when picking up finished code
- Checkpointing: a clear "building complete" signal lets you stash, review, or branch-switch before committing
- Scope control: each sub-skill has tight, testable behavior instead of one 8-phase monolith

## Do NOT

- Skip `/building` Phase 1 (reverse-thinking) — that's where the "agent judges best practice for me" value lives
- Merge into one mega-skill — the gate between `/building` and `/ending` is intentional
- Push past a `/ending` Phase 1 🔴 finding because "it was already tested" — regression review exists for the "I missed it" case
