---
name: rehydrate
description: "Reload codebase texture after context loss, then verify the queued step still aims at the project's endgame before dispatching it. Use right after `/compact`, when resuming a session left idle, when returning from a long-running subagent or Codex delegation, or when the user says 「進入狀況」 / \"rehydrate\" / \"再走一遍\"."
argument-hint: "[active plan doc or task surface]"
---

# Rehydrate

`/compact` keeps the *narrative* and loses the **texture** — exact signatures, the wording of a
locked invariant, the import shape of the neighbouring file, the evidence that made the queued step
right. Texture is what makes the next file you write read as native rather than grafted on. This
skill rebuilds it, confirms the step still aims at the endgame, and hands off.

Ultrathink throughout: a detail missed here propagates into every task after it.

## 1. Re-read the checkpoint

Read `<repo-root>/MEMORY.md` as a file. The auto-injected copy and the post-compact summary are both
lossy projections; the file is the source of truth and wins any disagreement. Recover the exact
wording of:

- the project's stated **endgame principle** and any locked architecture decisions;
- current phase and next action;
- the invariants governing the active surface, cited by their own identifiers (`V-3`, `L-2`);
- the topic files whose index lines touch the active surface — read those files, not the index.

**Complete when** every claim you will rely on has been read from a file this turn, and each point
where the summary and `MEMORY.md` diverged is resolved in the file's favour.

## 2. Name the task surface

State without paraphrase:

- the plan doc being executed (absolute path);
- the queued next step — `/mattpocock-skills:to-spec` while still designing,
  `/mattpocock-skills:implement <plan>` once the plan is approved, `/ship` once implementation is
  done;
- the files that step will touch (absolute paths, from the plan's own task list, not the summary's
  paraphrase);
- the invariants and locked decisions governing those files, cited by identifier.

Any of these ambiguous → ask one focused question and wait. A wrong-surface ultrathink pass costs
far more than the question.

**Complete when** all four are named concretely and the file paths exist.

## 3. Rebuild texture

Read **whole files**. A grep confirms a hypothesis; only whole-file reading surfaces the texture —
import shape, neighbouring test fixtures, naming convention, base-class behaviour — that decides
whether the next file looks native. Read in parallel, in this order:

1. the exact files in the plan's task list (Create / Modify / Test);
2. their directory siblings, for local pattern absorption;
3. the base class or shared utility the new code will subclass or call;
4. the plan or ADR section for the queued step specifically — skim what already shipped;
5. the most recent ship summary in `MEMORY.md`, which carries the invariants that locked in last.

**Complete when** you could write the next file from the surrounding code's muscle memory without
consulting the plan again.

## 4. Endgame check

Resolve the project's endgame principle from its own `CLAUDE.md` / `AGENTS.md` / `docs/principles.md`
(step 1 already recovered it). Absent an explicit principle, use best practice for the domain and
say that the framing is implicit.

Hold each meaningful decision in the queued step against it:

- Is this the single best-practice version, or a transitional shim?
- Does it add back-compat scaffolding, parallel `v2` / `enhanced_*` / `_old_*` naming, deprecated
  re-exports, or speculative-future hooks?
- Is it consistent with the cited invariants and the project's architectural layering?
- Does it stay clear of the anti-patterns this project has explicitly banned?

Uncertain counts as a fail. A fail means **surface the tension** in plain language with file:line
evidence, framed as the user's decision: "the plan defers X to phase N because R — still acceptable,
or should this phase widen to make it endgame-correct now?" Then wait. Amending the plan, accepting
the deviation with a recorded reason, and aborting are all the user's calls.

**Complete when** every decision in the queued step has an explicit pass, or the tension is on the
table with evidence and the user has answered.

## 5. Hand off

Confirm in ≤5 sentences of zh-tw: the plan doc, the queued step, the single most load-bearing
invariant it preserves, and any tension the user accepted. The user already read the plan — they
invoked rehydrate so the next step starts from live context, not so the plan gets re-pitched.

Then dispatch `/mattpocock-skills:to-spec` or `/mattpocock-skills:implement` directly. `/ship` is
user-invoked — name it as the next step and stop there.

**Complete when** the confirmation is printed and either the design/implement step is running or the
`/ship` handoff was stated.

## Language

zh-tw prose. Technical tokens stay English — file paths, function names, slash commands, ticket IDs,
SHAs, library names.
