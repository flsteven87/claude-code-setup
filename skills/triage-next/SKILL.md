---
name: triage-next
description: Use after /latest to autonomously pick the single highest-value noise-reducing topic off the board, ramp on it, and drive it to one of three terminal states — spec a contract ticket, confirm an already-ready contract for dispatch, or deep-review partial work for closing. Triggers on '/triage-next', '清板', '降噪選題', '下一步收什麼', '挑一題收尾', '接下來收哪個', '幫我選一題推進', 'what should I close next', or right after /latest when the user wants the next move chosen AND driven automatically rather than just listed. Selects by open-loop reduction > momentum > delegatability. Cites the ticket-contract SSOT and ends with a /narrate-glance report. This is NOT /strategic-next (that is big-bet leverage analysis for a human to choose from) — triage-next is autonomous board-clearing that runs the chosen work forward by itself.
---

# triage-next — autonomous board-clearing → contract / dispatch / close

`/latest` leaves memory synced to ground truth. `triage-next` is what you run next when you want the machine to **pick the most worthwhile thing to close and drive it forward**, not just hand you a list.

The skill owns three novel things: a **selection** rubric, a quick **ramp**, and a **router** that sends the chosen work to the right treatment. Everything heavy — distilling the end-state, drafting contract tickets with independent push-back, reviewing code, writing the report — is delegated to skills that already exist (`reverse-thinking`, `topic-to-tickets`, `code-review`, `narrate-glance`). Keep this skill a thin spine; resist re-implementing what those own.

## Why "noise reduction" is the objective

The board accumulates open loops: PRs that merged but left branches, tickets started and stalled, chains where one rung shipped and the next is unspecced, well-formed tickets nobody dispatched. Each is cognitive drag. The fastest way to a legible board is to close loops in priority order — and crucially, the *kind* of loop determines the *closing move*. That is why selection and routing are the whole job.

Priority is **B > C > A**, chosen because B and C are decidable from objective git/Linear/PR signals — so the selector can pick confidently on its own — while A needs judgment:

- **B — open-loop / WIP reduction (primary).** Close the half-open things.
- **C — momentum (secondary).** Prefer the smallest thing that ships value.
- **A — delegatability (tertiary).** Prefer what most readily becomes a clean contract for Joi/TARS.

## Pipeline

```
/latest (memory fresh)
   │
   ▼
━━ STAGE 1 ━━ SURVEY + PICK + CLASSIFY                 [autonomous → then GATE]
   • List every current 大主題 + one line each
   • Rank by B>C>A ordered criteria → select one
   • Classify the topic's next actionable unit → propose branch ①/②/③
   █ GATE (zh-tw): landscape + pick + next unit + proposed route + why-it-won
                   → user confirms, re-picks, or re-routes
   │
   ▼ (confirmed)
━━ STAGE 2 ━━ route by lifecycle state
   ├─① TRIAGE       no contract yet  → build one
   │     RAMP → reverse-thinking(distill) → karpathy lens → topic-to-tickets
   ├─② READY        already a good contract, no code  → confirm + signal dispatch
   │     Definition-of-Ready check → "可直接交 Joi/TARS"   (no mutation)
   └─③ PARTIAL      code exists, needs finishing  → review + advise
         /code-review (deep) + 收尾建議                    (no mutation)
   │
   ▼ (all branches)
REPORT — /narrate-glance: 5 sentences + diagram, dual-axis (solved / remaining)
```

Only outward-facing actions are gated: the Stage 1 gate, plus — for branch ① — the mutation gate that `topic-to-tickets` already owns. Branches ② and ③ make no mutation. The only other interrupt is the escape hatch below.

## When to use / when not

- **Use** right after `/latest`, or whenever the user wants the next move *chosen and driven*, not just analyzed.
- **Not** `/strategic-next` — that asks "what is the highest-leverage bet?" and hands options to a human. This skill assumes the goal is to clear the board and runs the chosen work itself. (End-state: this skill is expected to eventually replace `/strategic-next`; until then they coexist with distinct jobs.)
- **Not** `/latest` — that syncs memory. This consumes a freshly-synced memory; if memory looks stale, run `/latest` first.

## Stage 1 — survey, select, classify

### Candidate pool
The freshly-`/latest`-synced `MEMORY.md` already groups work into chains / clusters / epics (its Now + Active Backlog sections + chain pointers). Read that structure as the topic skeleton, then verify and augment against live signals: `gh pr list`, Linear `started`/`Todo`, `git branch -vv`. Group at the level of **大主題** — chain / epic / ticket-cluster / incident class — not fifty loose tickets.

### Selection — ordered criteria, not a numeric score
Rank by **B**, break near-ties by **C**, then **A**. Do **not** invent magic-number weights — hardcoded thresholds read as precision theater and the user has flagged that lesson before. Reason through the signals and *show which ones fired* at the gate, so the pick is legible rather than a black box.

- **B — open-loop severity:** an open PR (especially own / stalled / mergeable-but-unmerged); a Linear ticket `started`/`In Testing` with no recent commits (stalled WIP); a stale or merged-but-undeleted branch; a partial chain whose finished rung blocks its successors; few "steps-to-fully-closed".
- **C — momentum:** small estimated size; a crisp definition of done; low blast radius (does it touch schema / auth / public API?); already unblocked. **Lane feeds this** — an `express`/`standard` item outranks a `heavy` one.
- **A — delegatability:** already is, or quickly becomes, a clean contract; mechanical pattern-application over judgment; self-contained.

### Classify — on the topic's *next actionable unit*
A chain's children can sit in different states, so classify the next actionable unit, not the whole chain (e.g. for a materializer chain whose R3.3 just shipped, the next unit is R3.4).

```
Is there code already written for this unit?  (open PR commits / WIP branch / half-merged successor)
├─ YES → ③ PARTIAL   (code exists → review + finish)        ← code-exists wins
└─ NO
     └─ Is it already a best-practice contract?  (run Definition of Ready, see Stage 2 ②)
          ├─ YES → ② READY    (dispatch-ready)
          └─ NO  → ① TRIAGE   (build the contract)
```

### Stage 1 gate (zh-tw)
Present, in Traditional Chinese: the full landscape (each 大主題 one line + current state); the highlighted pick and its next actionable unit; the proposed branch; and **why it won** — the specific B/C/A signals that fired. Then stop. The user confirms, re-picks another topic, or re-routes. This is the one upfront human gate; everything after runs autonomously until an outward action or the escape hatch.

## Stage 2 — route to the closing move

These skills are invoked through the Skill tool, which loads them into the *same* context — so the ramp findings and the distilled end-state carry forward without serialization. Hand each downstream skill the context you already gathered rather than making it re-derive.

### Branch ① — TRIAGE (no contract yet → build one)
1. **RAMP** — read the unit's ticket(s), the relevant code, and recent commits; produce a tight situation brief (this doubles as the ground truth you hand forward).
2. **`reverse-thinking` (distill mode)** — end-state in one sentence + a diagram + 3–5 invariants. This is the north star.
3. **`karpathy-guidelines` lens** — collapse the end-state to the *smallest correct change*: surgical scope, no speculative additions, no overcomplication.
4. **`topic-to-tickets`** — hand it the confirmed scope (from the Stage 1 gate), the RAMP ground-truth cites, and the north star, noting these are already settled so it fast-forwards its own scope-confirm / ground-truth / end-state-distillation and starts at independent push-back. It produces contract ticket(s) per the contract SSOT (see below) and owns the mutation gate. Terminal: contract ticket(s) in Linear, ready to hand off (the user dispatches).

### Branch ② — READY (already a contract, no code → dispatch)
Run the existing ticket through the **Definition of Ready** in `docs/architecture/ticket-contract/README.md` (outcome observable / scope bounded / acceptance testable / evidence-depth a.k.a. lane assigned / unknowns separated / TARS can independently gate). If it passes, tell the user it is dispatch-ready and they can hand it to Joi/TARS — **make no mutation**; dispatch is the user's action. If it fails any item, it was misclassified: say so plainly and drop to branch ①.

### Branch ③ — PARTIAL (code exists → review + finish)
Invoke `/code-review` in its deep mode against the existing code or PR, then add finishing advice: which findings to fix, what deliverables remain, the risks, and how to close. **Make no mutation** — this branch is analysis. If the remaining work is substantial, you may suggest folding it into a branch-① finishing contract, but leave that as a recommendation.

## The contract is an existing SSOT — cite, don't reinvent
The canonical ticket contract lives in **`docs/architecture/ticket-contract/`** (README = policy + Definition of Ready; `ticket-template.md` = the template, with a compact and a full form). Branch ① produces against it; branch ② checks against it. **Cite it; never duplicate or fork the schema** — a second copy would drift. Pick the **compact** template for `express`/`standard` lanes and the **full** template for `heavy`, so contract weight stays proportional to risk rather than uniformly heavy.

## Escape hatch — `human_decision_needed`
Autonomy stops mid-flow only when the work hits a genuine human-owned decision. Use the contract policy's own categories: **product, business, credential, irreversible-data, or security-posture**. When you hit one, surface it as `human_decision_needed: yes:<reason>` and wait. Everything else — selection, ramp, routing, review — you resolve yourself; do not manufacture check-ins outside the Stage 1 gate, the branch-① mutation gate, and these five categories.

## Final report — `/narrate-glance`
Every branch ends by invoking `narrate-glance`: a ≤50-line, 5-sentence + diagram report, dual-axis — **what's SOLVED** (concrete impact + mechanism) and **what's REMAINING** (boundary + the next concrete action). High-level, but it must name the one thing that matters. This is the deliverable the user reads; the rest is machinery.

## Edge cases
- **Clean board** — no open loops worth closing: say so and stop. Don't manufacture work.
- **Mixed-state chain** — resolve to the single next actionable unit for the branch decision; list the rest in the landscape so nothing is hidden.
- **User override at the gate** — proceed with their topic/route, not yours.
- **Codex unavailable inside `topic-to-tickets`** — inherit its honest fallback: label that the rescue subagent stood in; never claim "Codex confirmed" when it didn't.

## Communication discipline
- The Stage 1 gate and the final report are in **Traditional Chinese**; code, paths, identifiers, and log lines stay in English. (Matches the rest of this user's skill surface.)
- Prefer "I read X at `file:line`" over "I think X" — selection and classification claims should rest on signals you actually observed, not on memory, which lags merges.
