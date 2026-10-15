# Audit an existing plan

Reserve this for work whose shape is still negotiable: multi-milestone plans, hard-to-revert
architecture decisions, milestone orders driven by ease rather than value, or a 現狀 nobody has
re-checked in a while. A single-PR feature or a scoped linear task is past the point where this
pays; say so in one line and stop.

## 1. Distill the endgame

Write the endgame record from the plan's own vision. When the vision will not fit the sentence,
the plan has nothing to be audited against: switch to [forge.md](forge.md) and audit afterwards.

## 2. Check preconditions against evidence

Derive the preconditions the endgame needs and find each one's current state in evidence read
this turn. A precondition the plan does not cover is a gap. A plan assumption the evidence
contradicts is ranked by what it breaks:

- **load-bearing:** silent failure, dead tests, wasted work, or a deliverable nobody can use;
- **scope-shifting:** the plan still works but must grow or shrink;
- **cosmetic:** wording or ordering only.

Absent dimensions count as gaps too: vision clarity, architectural direction, validation signal in
the first milestone, measurement, risk, rollback or reversibility per milestone (traced to a
mechanism, not asserted), and declarative rather than scattered scope gating.

## 3. Red-team the load-bearing claims

List what the plan asserts as true about the user, the problem, the constraint, the mechanism, and
the timeline. Keep the load-bearing claims: the ones whose failure kills the plan. For each, state
its steelman (the strongest reason it might be true), then attack that version and write the
result as **Fails if ___**, concrete and falsifiable.

Rank by impact if wrong × likelihood of being wrong × cheapness to test. A claim the plan already
backs with evidence, or one that survives its steelman, is reported as holding. For the top three
to five, give the operator something to do:

- **Fails if:** the precise condition that breaks the plan
- **Evidence to get:** the specific data, query, file, or conversation that confirms or kills it
- **Kill criterion:** the threshold at which to stop or change course
- **Cheapest test:** the smallest experiment that moves the belief

## 4. Move the plan

Recommend by moving the plan, not rewriting it: keep what delivers the endgame; reorder so the
cheapest test of the top kill-assumption and other validation signal come first; insert a missing
precondition as an explicit first milestone; reduce work that strengthens components the endgame
deletes; defer or delete work that repeats a known bug class.

## 5. RISK verdict

One line `RISK: LOW|MEDIUM|HIGH`, one line of rationale, and at most one gap that would escalate it.

- `LOW`: no load-bearing contradiction, no absent dimension, at most five files, and no schema,
  auth, dependency, or public API change.
- `MEDIUM`: a scope-shifting contradiction or one recoverable absent dimension.
- `HIGH`: a load-bearing contradiction, an architecture assumption the evidence contradicts, a top
  kill-assumption with no test before the work it guards, or several absent dimensions.

## Reply shape

Target and branch line → endgame record → contradictions and gaps (load-bearing first, each with
its citation) → ranked kill-assumption cards → what holds → the moved plan → RISK block → two or
three directions.

---

Step 3 adapts `strategy-red-team` from [phuryn/pm-skills](https://github.com/phuryn/pm-skills),
MIT License, Copyright (c) 2026 Pawel Huryn.
