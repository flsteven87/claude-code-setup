---
name: reverse-thinking
description: "Audit a plan, spec, or roadmap against what the endgame requires rather than against its own framing. Use before building non-trivial pre-planned work or when the user asks whether a plan is best practice, 「逆向思考」, 「戰略檢視」; `--distill` sets the end-state north star for a topic with no plan yet."
argument-hint: "[plan/spec path] [--distill]"
---

# Reverse Thinking — 從終局倒推檢視計畫

A plan is anchored on tasks and milestones, so a clean plan can drift from the 終局 while its own
narrative hides what the endgame needs. Reverse the order: distill the endgame, derive what must be
true for it, check that against the codebase, and judge the plan by its distance from there.

Reserve this for work whose shape is still negotiable: multi-milestone plans, hard-to-revert
architecture decisions, milestone orders driven by ease rather than value, or a 現狀 nobody has
re-checked in a while. A single-PR feature or a scoped linear task is past the point where this pays.

## Distill the endgame

Compress the whole vision into one sentence of real user experience, one diagram of the loop that
must exist in production, and three to five invariants that must always hold. Failing to fit the
sentence means the vision is not distilled yet. `--distill` stops here and hands the north star to
`/mattpocock-skills:grill-me`.

## Check the plan against it

Derive the preconditions the endgame needs and find each one's current state in the codebase, read
from files this turn; the plan's description of the 現狀 is a claim, not evidence. A precondition
the plan does not cover is a gap. A plan assumption the code contradicts is ranked by what it
breaks: load-bearing (silent failure, dead tests, wasted work), scope-shifting, or cosmetic. Absent
dimensions count as gaps too: vision clarity, architectural direction, validation signal in the
first milestone, measurement, risk, rollback per milestone, and declarative rather than scattered
scope gating.

Recommend by moving the plan, not rewriting it: keep what delivers the endgame, reorder to bring
validation signal forward, insert a missing precondition as an explicit first milestone, reduce work
that strengthens components the endgame deletes, and defer or delete work that repeats a known bug
class.

## RISK verdict

End with a risk verdict the user can act on: one line `RISK: LOW|MEDIUM|HIGH`, one line of
rationale, and at most one gap that would escalate it.
`LOW` needs no load-bearing contradiction, no absent dimension, at most five files, and no schema,
auth, dependency, or public API change. `MEDIUM` has a scope-shifting contradiction or one
recoverable absent dimension. `HIGH` has a load-bearing contradiction, an architecture assumption
the code contradicts, or several absent dimensions.

## Done

The verdict block is present, every load-bearing contradiction cites a file and line read this
turn, and the response ends with two or three concrete next-step directions for the user to choose;
the direction is theirs.
