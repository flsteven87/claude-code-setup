---
name: build
description: Use when you have a roughly clear feature/issue/topic and want a structured path from idea to working implementation. Triggers on '/build', 'build this feature', '幫我從頭蓋'.
---

# Build — Idea to Implementation

```
reverse-thinking(distill) → superpowers:writing-plans → superpowers:subagent-driven-development
```

If intent is unclear, invoke `brainstorming` skill BEFORE `/build` — not inside it. One skill, one job.

**User-facing output: zh-tw** (per CLAUDE.md). SKILL structure stays English.

## Phases

1. **Distill** — `Skill reverse-thinking` with mode=distill. Print the north star (1-sentence vision + architecture diagram + 3–5 invariants).
2. **Plan** — `Skill superpowers:writing-plans` using the north star. Print the resulting plan path.
3. **Implement** — `Skill superpowers:subagent-driven-development` using the plan. Honor its internal review checkpoints — do not suppress them.

## Default behavior: run end-to-end, no asking

Run all three phases without stopping. Log a 1-line summary per phase transition so the user can scan progress.

The user has already opted into the pipeline by invoking `/build` — do not re-confirm direction at every step. Trust the sub-skills.

## Stop only when (objective triggers, not preference)

- A sub-skill blocks, errors, or explicitly requests user input
- About to violate a 🔴 rule declared in project `CLAUDE.md`
- Distill output exposes a fundamental wrong-problem signal (architecture or invariants contradict stated intent in a way no plan can fix)

When stopping, print: current phase, the specific trigger, and the minimal question needed to unblock. No multi-option checkboxes.

## Completion

When all three phases succeed, print this exact signal so `/ship` (or the user) can detect end-of-pipeline:

```
build complete — plan: <path>
```

## Failure

On any phase failure: stop, print which phase, why, and artifacts produced so far. Do not auto-retry. Do not skip phases.
