---
name: rehydrate
description: Use right after `/compact`, or when situational awareness is suspect (resuming after a long pause, returning from a long-running subagent, user says 「進入狀況」 / "rehydrate" / "再走一遍"). Forces a deep ultrathink-grade re-read of MEMORY.md, the active plan doc, and the codebase files the next step will touch — then runs an endgame best-practice check against the project's stated principle (Contextra: Single Elegant Endgame) before handing off to `/writing-plans` or `/implement`. If any check fails, stops and surfaces the tension with file:line evidence rather than silently proceeding. NOT a memory-rewrite tool (use `/latest`), NOT a fresh-start summarizer (use `/catchup`).
---

# /rehydrate — Post-compact context reload + endgame check

`/compact` keeps the *narrative* of what happened but lossily compresses the *texture* of the codebase. Function signatures get smoothed, locked invariants get paraphrased, "I was about to do X" survives without the surrounding evidence that made X right. This skill forces a deliberate re-read before any further writing, then confirms the next step still aims at the endgame before dispatching it.

**Announce at start:** "I'm using the rehydrate skill to reload context and verify endgame alignment before continuing."

**Reasoning mode:** ultrathink throughout. The cost of a missed detail at this stage propagates through every subsequent task.

## When this is the right tool

Default trigger: immediately after `/compact`. Also valid when:
- Resuming a session after >1 hour idle
- Returning from a long-running subagent / Codex delegation
- The user says 「進入狀況」/ "reorient" / "rehydrate" / "再走一遍"

**Not** the right tool for:
- Fresh-session startup with no prior context → `/catchup` or `/latest`
- Trivial follow-ups in the same context window where memory is fresh
- Memory needs full sync + restructure → `/latest`
- Git state cleanup → `/git-state-audit`

## Workflow

### 1. Re-read MEMORY.md fresh

The system auto-injects MEMORY.md, but the post-compact *summary* may have lossily restated it. Read the actual file. Recover precise wording of:

- **Highest Priority Principle** + **Locked Architecture Decision**
- **Current Phase** + **Next** — these change session-to-session
- **Explicit DO-NOTs** (V-X invariants, locked decisions L-N)
- The **Memory Files** entries relevant to the active task surface (read the topic files themselves, not just the index line)

When the compacted summary and MEMORY.md diverge, MEMORY.md wins.

### 2. Identify the active task surface

Name precisely, no paraphrase:

- **The plan doc being executed** (absolute path under `docs/plans/...` or equivalent)
- **The slash command queued next** — `/writing-plans` if still designing, `/implement <plan>` if plan is approved and ready to execute, `/ship` if implementation is already done and we're heading to merge
- **The files the next step will touch** (absolute paths; do not trust the summary's paraphrase)
- **The invariants and locked decisions that govern those files** — cite by section / anchor / V-X / L-N

If any of these is ambiguous, **stop and ask one clarifying question before reading further**. Wasting an ultrathink pass on the wrong surface is more expensive than one clarifying question.

### 3. Ultrathink the codebase

Read **whole files**, not greps. Greps confirm a hypothesis; whole-file reading reveals the pattern texture — import shape, neighbouring test fixtures, function-naming conventions, repository base-class behaviour — that determines whether the next file you write looks native or grafted on.

Prioritize, in order:

1. The exact files listed in the active plan's task list (Tasks → Files → Create / Modify / Test)
2. Sibling files in the same directory (local pattern absorption)
3. The repository base class / shared utility the new code will subclass or call
4. The plan / ADR section for **the next step specifically** (skim past sections already shipped; deep-read what's queued)
5. The most recent ship summary in MEMORY.md's `Recent Ships` — load-bearing for invariants that just locked in

Parallelize the reads where possible. The goal is to come out of this step able to write the next file from muscle memory of the surrounding code, not by referring back to a plan.

### 4. Endgame best-practice check

Verify the plan / next implementation step against the project's stated **endgame principle**.

- **Contextra**: "Single Elegant Endgame — One version. Always current. No legacy. No compromises." (CLAUDE.md Part 1)
- **Other projects**: their CLAUDE.md / AGENTS.md / `docs/principles.md`. If no explicit principle exists, fall back to "best practice for this domain" and note the implicit framing.

For each meaningful decision in the next step, ask:

- Does it represent the **single best-practice version**, or is it a transitional shim?
- Does it introduce backward-compat scaffolding, parallel `v2` / `enhanced_*` / `_old_*` naming, deprecated re-exports, or speculative-future hooks?
- Is it consistent with the locked V-X invariants and the project's architectural layering (e.g. 4-layer API → Service → Repository → DB)?
- Does it avoid pipeline-design / data-access / API-design anti-patterns the project has explicitly banned?

Every answer "yes" → proceed to step 5.

Any answer "no" or "not sure" → **stop and surface the tension in plain language with file:line evidence**. Frame as a user-owned decision: "the plan defers X to phase N for reason R; still acceptable, or should this phase widen to make it endgame-correct now?"

**Never silently downgrade scope to make a deferred concern go away.** Surfacing tension is the whole point of this step.

### 5. Handoff

If checks 1-4 all passed:

- Print a **≤ 5-sentence** confirmation in zh-tw naming: the plan doc + the queued slash command + the single most-load-bearing invariant the next step preserves + any deferred-but-acknowledged tension.
- Then invoke the queued slash command (`/writing-plans` for design, `/implement` for execution, `/ship` for merge). Do **not** re-narrate the plan — the user already read it; they invoked rehydrate so the next step doesn't start from a stale snapshot, not so it gets re-pitched.

If any check failed:

- Stop. Surface the specific tension in 1-3 sentences with file:line evidence.
- Offer the user the explicit choice: amend the plan, accept the deviation with documented reason, or abort.
- Do NOT dispatch the next slash command until the tension is resolved.

## Communication

All user-facing output in zh-tw. English reserved for technical tokens only — file paths, function names, slash command names, ticket IDs, commit SHAs, library names. Don't translate technical tokens into Chinese.

## Anti-patterns

| Don't | Why |
|---|---|
| Trust the post-compact summary verbatim | It's a lossy projection; the source files are the SSOT |
| Use greps as a substitute for whole-file reading | Greps confirm a hypothesis but won't reveal pattern texture |
| Skip step 4 because "the plan is already written" | Endgame check IS the point — if the plan were already endgame-correct, the user wouldn't be asking for an explicit recheck |
| Re-narrate the plan back to the user before dispatching | They already read it; confirm + go |
| Do the next step's actual work inside this skill | Rehydrate ends with handoff, not implementation |
| Skip clarifying questions to "save time" | Wrong-surface ultrathink is more expensive than one question |
| Silently downgrade plan scope to bypass an endgame-check fail | The point is to surface tension, not absorb it |

## Relationship to adjacent skills

- **`/catchup`** — fresh-session orientation from `git` + memory + minimal file reads. Lighter than rehydrate; no endgame check, no plan-doc deep-read, no auto-dispatch. Use when context is genuinely empty.
- **`/latest`** — full memory rewrite + sibling consolidation. Much heavier than rehydrate; runs in zh-tw and rewrites MEMORY.md against ground truth. Use when memory has drifted, not just because of compact.
- **`/handoff`** — end-of-session surgical memory update. Opposite end of the session: rehydrate runs at the start, handoff runs at the close.
- **`/writing-plans`** — the dispatch target when we're still in design phase.
- **`/implement`** — the dispatch target when the plan is approved.
