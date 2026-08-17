---
name: rehydrate
description: "Reload codebase texture after context loss, then verify the queued step still aims at the project's endgame before it runs. Use right after `/compact`, when resuming a session left idle, when returning from a long-running subagent or Codex delegation, or when the user says 「進入狀況」 / \"rehydrate\" / \"再走一遍\"."
argument-hint: "[active plan doc or task surface]"
---

# Rehydrate

`/compact` keeps the *narrative* and loses the **texture** — exact signatures, the wording of a
locked invariant, the import shape of the neighbouring file, the evidence that made the queued step
right. Texture is what makes the next file you write read as native rather than grafted on. This
skill rebuilds it, confirms the step still aims at the endgame, and hands off.

Ultrathink throughout: a detail missed here propagates into every task after it.

## 1. Re-read the checkpoint

Resolve the active worktree with `git rev-parse --show-toplevel`, then resolve the primary checkout
from the first `worktree` record in `git worktree list --porcelain`. Read
`<primary-checkout>/MEMORY.md` as a file: the auto-injected copy and the post-compact summary are
both lossy projections, and the file wins any disagreement. Recover the exact wording of:

- the keyed entry under `## Active Workstreams` that owns the active surface — its objective, state,
  next action, blocker, and Git anchor;
- the `## Current State` facts that constrain that entry;
- the `## Durable Pointers` whose targets touch the active surface — read those targets, not the
  pointer line.

`MEMORY.md` is an operational cache, not authority. Take the endgame principle, locked architecture
decisions, and named invariants from their owners — the repository's `CLAUDE.md`, `AGENTS.md`,
`CONTEXT.md`, its ADRs, or the plan doc — and treat memory's version as a lead to verify.

**Complete when** every claim you will rely on has been read from a file this turn, each point where
the summary and `MEMORY.md` diverged is resolved in the file's favour, and every architecture claim
is attributed to its owning file rather than to memory.

## 2. Name the task surface

State without paraphrase:

- the plan doc being executed (absolute path);
- the queued next step — `/mattpocock-skills:to-spec` while still designing,
  `/mattpocock-skills:implement <plan>` once the plan is approved, `/ship` once implementation is
  done;
- the files that step will touch (absolute paths, from the plan's own task list, not the summary's
  paraphrase);
- the invariants and locked decisions governing those files, each attributed to the file that owns it.

Any of these ambiguous → ask one focused question and wait. A wrong-surface ultrathink pass costs
far more than the question.

**Complete when** all four are named concretely, every Modify and Test path resolves on disk, and
every Create path names a directory that exists.

## 3. Rebuild texture

Read **whole files**. A grep confirms a hypothesis; only whole-file reading surfaces the texture —
import shape, neighbouring test fixtures, naming convention, base-class behaviour — that decides
whether the next file looks native. Issue the reads within one tier together, then move to the next:

1. the exact files in the plan's task list (Create / Modify / Test);
2. for each Create target, the two closest neighbours in its directory — the nearest existing file
   of the same kind and that file's test — for local pattern absorption;
3. the base class or shared utility the new code will subclass or call;
4. the plan or ADR section for the queued step specifically — skim what already shipped;
5. the selected workstream's own pointers in `MEMORY.md`, which name the constraints that locked in
   last.

**Complete when** every file in the plan's task list has been read whole this turn, along with the
base class or shared utility each new file will subclass or call, and you can state the local
convention the next file must follow — its import shape, its test fixture, its naming pattern —
without reopening them.

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

Then name the queued step as the standalone command the human types — `/mattpocock-skills:to-spec`,
`/mattpocock-skills:implement <plan>`, or `/ship` — and stop there. All three are user-only: the
runtime expands the standalone command before its workflow is authorized, so reading a `SKILL.md`
to imitate one is not a substitute for the human invoking it.

**Complete when** the confirmation is printed and the next standalone command is named.

## Language

zh-tw prose. Technical tokens stay English — file paths, function names, slash commands, ticket IDs,
SHAs, library names.
