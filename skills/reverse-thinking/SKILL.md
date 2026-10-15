---
name: reverse-thinking
description: "Work backwards from the endgame. Audits an existing plan, spec, or roadmap against what the end state requires; when no plan exists yet, forges the end state with a press release and hard FAQs before anything is built. Use for 逆向思考, 戰略檢視, working backwards or a PRFAQ, before building non-trivial planned work, when choosing what to build, or when the user asks whether a plan is best practice."
---

# Reverse Thinking — 從終局倒推

A plan is anchored on its tasks and an idea on its solution, so either can look sound while its
own narrative hides what the endgame needs. Reverse the order: fix the endgame first, then judge
everything by its distance from there.

## Find the target

The user invokes this with no arguments. Take the target from context, in this order: the plan,
spec, roadmap, or idea discussed most recently in this conversation; a file the user named; the
project's record of current work (its `MEMORY.md` active workstream, plan or spec documents, the
owning topic or ticket). Open with one line naming the target and the branch it puts you on, then
continue; the user redirects if you picked wrong. Ask only when context names no target at all.

- **Audit** when a plan exists: ordered work toward a stated outcome, such as milestones, a spec,
  a roadmap, or a queue of next actions. Read [references/audit.md](references/audit.md).
- **Forge** when there is a problem, topic, or idea but no plan, or when an audited plan's vision
  will not fit the endgame sentence. Read [references/forge.md](references/forge.md).

## The endgame record

Both branches converge on the same record:

- **Sentence:** one sentence of real user experience: who, and what changes for them.
- **Loop:** one diagram of the loop that must exist in production or in daily use.
- **Invariants:** three to five, each observable, binary or thresholded, and true whichever path
  reaches the end state.

A vision that will not fit the sentence is not distilled yet; that is a finding in itself.

## Evidence

A statement about the current state is evidence only when read this turn from its source: code,
data, the project's documents, or a primary external source. A plan's or idea's description of
the 現狀 is a claim to check. Every load-bearing finding cites the `file:line` or URL it was read
from. Label the rest as inference or unknown, and give each unknown the cheapest way to find out.

## Delivery

This skill reviews and plans; it changes nothing in the project. The reply carries the endgame
record, the verdict, and the directions. A full PRFAQ is long: write it to the session scratchpad
(or `/tmp` when none exists) and give its absolute path. Adding the result to the project's own
record (a topic document, spec, ADR, or ticket) is a follow-up direction the user chooses.

## Done

The branch's verdict is present, the endgame record is present, every load-bearing finding cites
evidence read this turn, and the reply ends with two or three concrete next-step directions. The
direction is the user's.
