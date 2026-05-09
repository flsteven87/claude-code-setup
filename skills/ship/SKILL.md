---
name: ship
description: Use when you want to take an idea or issue all the way to a shipped, documented commit in one autonomous run. Triggers on '/ship', 'ship this', 'take it from idea to commit', '從頭到尾做完'.
---

# Ship — End-to-End Pipeline

```
/ship = /build → /ending
```

`/build` (distill → plan → implement) then `/ending` (review → simplify → commit → handoff).

**User-facing output: zh-tw** (per CLAUDE.md). SKILL structure stays English.

## Topic resolution

- `/ship <topic>` — use the topic verbatim
- `/ship` (no arg) — read MEMORY.md `## Active Work` and auto-pick the top 🔴 item. No confirmation prompt — invoking `/ship` IS the consent.
- `/ship` (no arg) but MEMORY.md missing, or `## Active Work` absent, or no 🔴 item listed → stop and ask user for the topic (objective trigger, see Stop section).

## Execution

1. Invoke `Skill build` with the topic.
2. On `build complete` → invoke `Skill ending` immediately.
3. On `ending complete` → print:

```
ship complete
topic:   <topic>
commits: <sha1>..<shaN>
memory:  updated
```

## Default behavior

Run build → ending end-to-end. No mid-flow user prompts beyond what the sub-skills' own stop conditions impose.

**Output discipline:**
- *Phase-level progress* from sub-skills (north star, plan path, per-phase 1-liners) flows through — that is useful visibility.
- *Final completion reports* from sub-skills (`build complete — ...`, `ending complete — ...`) are internal sequencing signals. Absorb them; do NOT emit them to the user. The user sees only `/ship`'s own final summary below.

## Stop only when (objective triggers, inherited from sub-skills)

- A sub-skill blocks, errors, or explicitly requests user input
- `/build` halts at any phase → do NOT auto-start `/ending`. Report which phase broke.
- `/ending` halts at any phase → report which phase broke. Do not auto-rerun `/build`.
- `/ship` with no arg AND MEMORY.md `## Active Work` is missing or empty → stop and ask for the topic.

## Failure

Print which sub-skill and which phase failed, plus artifacts produced so far (plan path, commit hashes, etc.). Do not auto-retry. Do not skip the failed sub-skill.
