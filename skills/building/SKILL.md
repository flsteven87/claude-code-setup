---
name: building
description: Use when starting a new topic/issue/feature and want the full front-half pipeline — strategic sanity-check → intent clarification → plan → implementation with review checkpoints. Triggers on '/building', 'build this feature', 'start this work the right way', '幫我從頭蓋'.
---

# Building — Front-Half Pipeline

Runs 4 skills in sequence, with human gates at the two points where human judgment is load-bearing.

```
reverse-thinking → brainstorming → writing-plans → superpowers:executing-plans
      (judge)        (clarify)        (plan)             (implement)
```

## Mode Flag

Parse `$ARGUMENTS` for `--auto`:

- **Default (careful):** stop at every gate below, wait for user "go"
- **`--auto`:** proceed automatically IF reverse-thinking marks the task **LOW RISK** (see bar below). Otherwise **force careful mode** — do not respect `--auto` on risky work.

**LOW RISK bar (all must hold):**
- Scope ≤ 5 files
- No schema / migration / RLS changes
- No auth / security / secrets touched
- No new runtime dependency added
- No public API contract change

Any one violation → careful mode, regardless of flag.

## Phase 1 — Reverse Thinking (judge)

Invoke `Skill reverse-thinking` against the user's stated topic.

Output MUST include a risk verdict:
- `RISK: LOW` / `RISK: MEDIUM` / `RISK: HIGH`
- One-line rationale
- Any hidden assumptions flagged

**Gate:** In careful mode → stop, summarize verdict, ask user to confirm direction. In `--auto` + LOW RISK → proceed silently with a 1-sentence note.

## Phase 2 — Brainstorming (clarify)

Invoke `Skill brainstorming`. This skill is inherently interactive — it elicits intent, requirements, design.

**Gate:** Brainstorming decides when it's done. Do NOT shortcut this phase under `--auto` — clarified intent is a safety input to every downstream phase.

## Phase 3 — Writing Plans (plan)

Invoke `Skill writing-plans` with the clarified intent from Phase 2.

**Gate:**
- Careful mode: present plan, wait for user approval
- `--auto` + LOW RISK: proceed if plan stays within LOW RISK bar. If plan crosses the bar (e.g. adds dependency, touches schema) → revert to careful mode and wait

## Phase 4 — Executing Plans (implement)

Invoke `Skill superpowers:executing-plans`. Honor its internal review checkpoints — do NOT suppress them under any mode.

## Completion

On success, print a handoff line:
```
building complete — ready for /ending
```

On failure mid-phase: stop, report the phase and the reason. Do NOT auto-retry past plan changes.

## Rules

- Each sub-skill is invoked via the `Skill` tool — follow whatever it returns exactly
- Do not merge phases to save tokens — separation is the point
- If user says "skip to phase N" → respect it but warn once that skipped phases may cost more later
