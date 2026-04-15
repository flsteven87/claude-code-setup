---
name: building
description: Use when starting a new topic/issue/feature and want the full front-half pipeline — end-state distillation → intent clarification → plan → plan audit → constitution gate → subagent-driven implementation. Triggers on '/building', 'build this feature', 'start this work the right way', '幫我從頭蓋'.
---

# Building — Front-Half Pipeline (2026 Spec-Driven)

Six phases with two reverse-thinking touchpoints — one to **open** (set north star), one to **close** (audit the plan). Aligned with 2026 spec-driven best practice (SpecKit Pre-Implementation Gate, Kiro three-doc flow, Anthropic Ultra Plan Deep).

```
reverse-thinking(distill) → brainstorming → writing-plans → reverse-thinking(audit) → Constitution gate → subagent-driven-development
       (north star)          (clarify)        (plan)             (judge + RISK)          (CLAUDE.md)            (implement)
```

## Mode Flag

Parse `$ARGUMENTS` for `--auto`:

- **Default (careful):** stop at every gate, wait for user "go"
- **`--auto`:** proceed automatically IF Phase 4 `reverse-thinking --mode=audit` returns `RISK: LOW`. Otherwise force careful mode regardless of flag.

The LOW RISK bar lives inside `reverse-thinking` Part F (scope ≤ 5 files, no schema/auth/dep/public API change). Do not re-implement the bar here.

## Phase 1 — Reverse Thinking: Distill (north star)

Invoke `Skill reverse-thinking` with **mode=distill**.

Output is only Part A: 1-sentence vision + architecture diagram + 3–5 invariants. No codebase audit yet (nothing to audit).

**Purpose:** catch "wrong problem" before spending tokens on clarification.

**Gate:** careful mode → show distilled north star, ask user "direction correct?". `--auto` → proceed with 1-sentence note.

## Phase 2 — Brainstorming (clarify)

Invoke `Skill brainstorming`, carrying Phase 1's invariants into the dialogue.

Brainstorming is inherently interactive (HARD-GATE inside it) — do NOT shortcut under `--auto`. Clarified intent is a safety input to every downstream phase.

Terminal state: spec written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.

**Override:** brainstorming's own terminal handoff says "invoke writing-plans next". Inside `/building`, **let `/building` drive Phase 3 invocation** instead — do not double-invoke.

## Phase 3 — Writing Plans (plan)

Invoke `Skill writing-plans` with the spec from Phase 2.

Output: `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` with bite-sized tasks.

**Gate:** present plan, wait for user approval in careful mode. In `--auto` continue to Phase 4 — the audit is the real gate, not this one.

## Phase 4 — Reverse Thinking: Audit (judge + RISK)

Invoke `Skill reverse-thinking` with **mode=audit** against the plan from Phase 3.

Full Part A–F output. Part F gives `RISK: LOW/MEDIUM/HIGH`.

**Gate:**
- `RISK: HIGH` → STOP. Show gaps + restructuring recommendation. User must resolve before continuing (usually loops back to Phase 3 to patch plan).
- `RISK: MEDIUM` → careful mode stops, `--auto` degrades to careful mode.
- `RISK: LOW` → proceed. `--auto` proceeds silently with 1-line note.

**Do not suppress Phase 4 under any flag.** This is the load-bearing gate in the pipeline.

## Phase 5 — Constitution Gate (agent config file)

Read the project's constitution file. The filename depends on which agent is running:

| Platform | Project file | Global file |
|---|---|---|
| Claude Code | `CLAUDE.md` | `~/.claude/CLAUDE.md` |
| Codex | `AGENTS.md` | `~/.codex/AGENTS.md` |
| Gemini CLI | `GEMINI.md` | `~/.gemini/GEMINI.md` |

**Resolution rule:** read whichever file(s) exist at the project root; if the agent has a known global equivalent, read that too. Don't require all three — read what's there. If none exist, print `constitution gate: no config file found, skipped` and proceed.

Print a checkbox summary against the plan:

- [ ] Respects project architecture rules (e.g. 4-Layer, layering conventions) if declared
- [ ] No Single-Elegant-Version violation (no V2 / _old / parallel version)
- [ ] No over-defensive coding / fallback additions
- [ ] Naming conventions followed
- [ ] No forbidden patterns (🔴 list in the config file)
- [ ] Project-specific gotchas checked (read `memory/gotchas.md` if present)

**Gate:** any unchecked item → STOP, ask user whether to patch plan or accept deviation (explicitly logged). `--auto` cannot bypass this.

This is cheap but critical. SpecKit calls it Pre-Implementation Gate; we call it Constitution Gate.

## Phase 6 — Implementation (fresh subagent per task)

Invoke `Skill superpowers:subagent-driven-development` (NOT `executing-plans` — fresh subagent per task is the 2026 best practice, prevents context pollution).

Honor its internal two-stage review checkpoints — do NOT suppress them under any mode.

**Fallback:** if the plan is ≤ 3 tasks AND Phase 4 returned `RISK: LOW`, `superpowers:executing-plans` (inline) is acceptable to save overhead. Any other case → subagent-driven.

## Completion

On success, print:

```
building complete — ready for /ending
spec:  <path>
plan:  <path>
risk:  <LOW|MEDIUM|HIGH>
phase: 6/6
```

## Failure & Resume

On any mid-phase failure: stop, print current state so resume is trivial:

```
building halted at phase N/6 — reason: <short>
next action: <exact next step>
artifacts so far: <paths>
```

Do NOT auto-retry past plan changes. Do NOT unwind upstream phases silently.

## Rules

- Each sub-skill is invoked via `Skill` tool — follow whatever it returns exactly
- Do not merge phases — separation is the point (each gate catches a different failure mode)
- `--auto` only flows through if Phase 4 returns `RISK: LOW`
- User says "skip to phase N" → respect it but warn once that skipped phases may cost more later
- Phases 1, 4 both use `reverse-thinking` but with **different modes** — never call it without a mode argument

## Cross-Platform Notes

This skill is shared across Claude Code, Codex, and Gemini CLI.

- **Skill invocation syntax** in this doc uses Claude Code convention (`Skill reverse-thinking`). Codex invokes skills via its `skill` tool; Gemini uses `activate_skill`. See `references/codex-tools.md` / `references/copilot-tools.md` in superpowers for the exact tool mapping — the agent adapts automatically.
- **Constitution file** is platform-specific (CLAUDE.md / AGENTS.md / GEMINI.md). Phase 5 resolves this at runtime.
- **`superpowers:subagent-driven-development`** requires the `superpowers` plugin installed on the current platform. If unavailable, fall back to `superpowers:executing-plans`, then to running tasks inline manually.
- **Sub-skills referenced** (`reverse-thinking`, `brainstorming`, `writing-plans`) are expected to exist in the user's global skill directory — they travel together as a bundle. If one is missing, `/building` halts at that phase with a clear message.

## Why Two Reverse-Thinking Touchpoints

| Touchpoint | Catches |
|---|---|
| Phase 1 (distill) | "Wrong problem" — building something that shouldn't exist |
| Phase 4 (audit) | "Right problem, wrong solution" — plan diverges from end-state |

Collapsing into one touchpoint trades away one of the two failure modes. The industry consensus (Kiro, SpecKit, Ultra Plan) all have structural equivalents of both touchpoints.
