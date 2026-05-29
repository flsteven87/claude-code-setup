# /triage-next — Design Spec

> **Status:** design (brainstorming output, pre-implementation).
> **Working name:** `triage-next` (provisional; `clear-next` is the alternate). Renaming the dir later is cheap.
> **Lifecycle:** user-level Claude skill design. Lives with the skill at `~/.claude/skills/triage-next/`. NOT a nr-platform product artifact → `docs/DOCS_POLICY.md` does not govern it. Absorbed into the skill's own SKILL.md on implementation; this DESIGN.md may stay as the skill's design record or be deleted once SKILL.md is self-explanatory.
> **Source conversation:** 2026-05-29 brainstorming session.

## 1 · Problem & goal

After `/latest` syncs memory to ground truth, the user wants an **autonomous** next move: pick the single highest-value "noise-reducing" topic off the board, get up to speed, and drive it to one of three terminal states — all with minimal human intervention, ending in a high-level `/narrate-glance` report.

The skill's reason to exist is the **selection + routing** logic. The heavy lifting (reverse-thinking, contract drafting + Codex push-back + Linear mutation, code review, the glance report) is delegated to **existing skills**. This skill is the orchestrator spine that selects, ramps, classifies, and composes.

## 2 · Selection objective (automation-first)

Priority **B > C > A**, chosen because B and C are decidable from objective git/Linear/PR signals (so the selector can pick autonomously and confidently), while A needs judgment.

- **B — open-loop / WIP reduction (primary):** close the half-open things. This is "降噪."
- **C — fast momentum (secondary):** smallest thing that ships value.
- **A — delegatability (tertiary):** how readily it becomes a clean contract for Joi/TARS.

This is deliberately a different objective from `/strategic-next` (max leverage / big bets). See §11 for strategic-next's disposition.

## 3 · Architecture — 2-stage / 3-branch router

```
/latest (memory fresh)
   │
   ▼
━━ STAGE 1 ━━ SURVEY + PICK + CLASSIFY                 [autonomous → then GATE]
   • List ALL current 大主題 + one-line each (absorbs strategic-next's survey DNA)
   • Score by B>C>A ordered criteria → select 1
   • Classify the selected topic's next actionable unit → propose branch 1/2/3
   █ GATE: landscape + pick + proposed route + why → user confirms (may override)
   │
   ▼ (confirmed)
━━ STAGE 2 ━━ route by lifecycle state:
   ├─① TRIAGE (no contract yet)
   │     RAMP → reverse-thinking(distill) → karpathy lens → topic-to-tickets
   │     (→ ground-truth + audit + Codex + internal mutation gate) → Linear contract → ready for Joi/TARS
   │
   ├─② READY CONTRACT (already a best-practice contract, no code yet)
   │     run Definition of Ready check → "可直接交 Joi/TARS" signal (NO mutation)
   │
   └─③ PARTIAL IMPL (code exists, needs closing)
         deep /code-review → 收尾建議 (findings + what's left + optional → fold into a finishing contract) (NO mutation)
   │
   ▼ (all three branches)
⑥ REPORT — /narrate-glance: 5 sentences + diagram, dual-axis (solved / remaining)
```

**Only outward-facing actions are gated.** Stage 1 gate (confirm pick/route) + Branch ①'s inherited topic-to-tickets mutation gate. Branches ②/③ produce no mutation (the user dispatches ② themselves; ③ is analysis). Escape hatch (§9) is the only other interrupt.

## 4 · Stage 1 — survey + score + classify

### 4.1 Candidate pool
- **Primary source:** the freshly-`/latest`-synced `MEMORY.md` — it already groups work into chains / clusters / epics (Now + Active Backlog + chain pointers). Read its structure as the topic skeleton.
- **Verify / augment:** open PRs (`gh`), Linear started/Todo, git stale branches.
- **Granularity:** 大主題 = chain / epic / ticket-cluster / incident class — not 50 loose tickets.

### 4.2 Selection — ordered criteria, NOT a numeric score
> No magic-number weights (Codex lesson in memory: "hardcoded thresholds = theater"). Rank by reasoning, and **show which signals fired** at the gate.

Sort primarily by **B**, break near-ties by **C**, then **A** (lexicographic). Signals per axis:
- **B (open-loop severity):** open PR (own / stalled / mergeable-unmerged); Linear started·In Testing with no recent commits (stalled WIP); stale branch; partial chain blocking its successors; "steps-to-fully-closed" (fewer = higher).
- **C (momentum):** estimated size (smaller = higher); clarity of done; blast radius (schema/auth/public-API?); already-unblocked. **Lane (§7) feeds this** — express/standard rank above heavy.
- **A (delegatability):** is/can-quickly-become a clear contract; mechanical vs judgment; self-contained.

### 4.3 Branch classifier — on the topic's **next actionable unit**
(A chain's topic may have children in different states; classify the next actionable unit, e.g. NEX-1034 chain → next unit = R3.4.)
```
Code already written? (open PR commits / WIP branch / half-merged successor)
├─ YES → ③ PARTIAL (code-review + finish)                 ← code-exists wins
└─ NO
     └─ Already a best-practice contract? (run Definition of Ready, §6)
          ├─ YES → ② READY (dispatch signal)
          └─ NO  → ① TRIAGE (build the contract)
```

### 4.4 Stage 1 gate shows
Full landscape (each topic one-line + current state); highlighted pick + next actionable unit + proposed branch; **why it won** (which B/C/A signals fired — not a black box). User may confirm / re-pick / re-route.

## 5 · Stage 2 — the three branches

- **① TRIAGE:** RAMP (read ticket+code+commits → tight brief) → `reverse-thinking` (distill: end-state sentence + diagram + invariants) → karpathy lens (collapse to smallest correct change) → `topic-to-tickets` (which does ground-truth + audit + Codex + Linear mutation per the ticket-contract template). Terminal: contract ticket(s) in Linear, ready to hand off.
- **② READY CONTRACT:** verify the existing ticket passes Definition of Ready (§6). If yes → tell the user it's ready and to hand it to Joi/TARS. **No mutation** — the user dispatches. If it fails any DoR item → it's actually a ① (downgrade and say so).
- **③ PARTIAL IMPL:** invoke `/code-review` (deep) on the existing code/PR + add finishing recommendations (remaining deliverables, risks, how to close). **No mutation.** Optionally suggest folding the finish work into a ① contract.

## 6 · Contract = existing SSOT (do not reinvent)

The canonical ticket contract is **`docs/architecture/ticket-contract/`** in nr-platform (README = policy, `ticket-template.md` = template). The skill **cites** it; it does not duplicate or fork it (DOCS_POLICY §4.2 SSOT + §10 citation).

- **Branch ① output** conforms to `ticket-template.md`. The skill picks **compact vs full template by lane** (§7): express/standard → compact; heavy → full → proportional weight, no bloat.
- **Branch ② rubric** = README's **Definition of Ready (6)** + **Final readiness checklist (5)**. Not a skill-invented rubric.
- **Assessment (settled):** the existing contract is NOT too heavy — it is already tiered (compact template + express lane) and weight scales with risk (karpathy-aligned). Automation removes the human drafting burden that made "heavy" a complaint. Keep as-is.

## 7 · Lane system (reused, not reinvented)
`express | standard | heavy` from the contract policy. Drives evidence depth + TARS gating, AND feeds C/A selection signals, AND selects compact-vs-full template. One concept, three uses — no parallel "size" metric.

## 8 · topic-to-tickets enhancement (the user's hard requirement)
Wire `topic-to-tickets` to the contract SSOT:
- Phase 6 (Linear mutation) **produces per `ticket-template.md`**, assigns a **lane**, and **gates on Definition of Ready** before mutating.
- Add an explicit **cite** to `docs/architecture/ticket-contract/` in the skill instructions.
- Rename its current `## Output contract` section → `## Audit deliverables` (it lists audit artifacts, not a ticket contract — removes the naming collision with the real contract).
- This upgrade benefits manual `topic-to-tickets` runs too, not only the orchestrated path.

## 9 · Escape hatch = `human_decision_needed`
Mid-flow, the skill interrupts the user ONLY when it hits a `human_decision_needed: yes` category from the contract policy: **product / business / credential / irreversible-data / security-posture**. Otherwise it runs to the Stage 1 gate (and Branch ①'s inherited mutation gate) without asking.

## 10 · Final report = `/narrate-glance`
Every branch ends by invoking `narrate-glance` style: ≤50 lines, 5 sentences + 1–2 ASCII diagrams, **dual-axis (what's SOLVED / what's REMAINING)**, high-level but pinpoints the key thing.

## 11 · strategic-next disposition
**Re-position, not retire** (user decision 2026-05-29). `/strategic-next` becomes the **forward-looking feature-exploration** tool — "what net-new features should we explore next" — explicitly EXCLUDING backlog / 待辦 items, which are now `triage-next`'s domain. Clean division of labor: `triage-next` clears the existing board; `strategic-next` explores net-new features. Once strategic-next sheds backlog prioritization their objectives no longer overlap, so coexistence is stable (no single-version conflict). The strategic-next rewrite itself is **deferred** ("可以之後優化") — this captures the decision; do the rewrite in a later pass.

## 12 · Composition seams
- Skill-tool invocation loads sub-skills into the **same context** (not subagents) → no serialization; RAMP cites + north star carry forward.
- Branch ① feeds `topic-to-tickets` a pre-filled context (scope confirmed at Stage 1, RAMP ground-truth, distilled north star) so it **fast-forwards** its Phase 1/2 + audit Part A and starts at Codex push-back. Branch ① inherits its Phase 5 mutation gate.
- Codex unavailable inside topic-to-tickets → inherit its honest fallback (label rescue-subagent; do not claim "Codex confirmed").

## 13 · Edge cases
- Clean board / no open loops → report it and stop.
- Selected chain has both ready + partial children → resolve to the single next actionable unit; list the rest in the landscape.
- User overrides pick/route at Stage 1 → proceed with their choice.
- Branch ② ticket fails Definition of Ready → downgrade to ① transparently.

## 14 · Out of scope / open questions
- Final skill name (`triage-next` vs `clear-next` vs other).
- Whether `/latest` should auto-suggest running this skill at its end (currently: separate manual invocation).
- Optional: add a one-line cross-ref in `ticket-contract/README.md` naming the automated producers (pure cross-reference; user to decide).
- Dispatch plumbing to Joi/TARS stays manual (user hands off); the skill only signals readiness. Reuses `project_joi_dispatch_plan` knowledge.
- **Branch ① + express lane:** does `topic-to-tickets`' mandatory Codex round scale down for tiny express contracts, or always run full? Proposed default: always run the independent challenge (it is the point of topic-to-tickets), but keep it brief for express. Confirm during implementation.
- Read `docs/audits/2026-05-22-hermes-5day-audit.md` during implementation to harvest concrete ticket-quality → automation-success lessons.

## 15 · Implementation outline (files)
- **NEW** `~/.claude/skills/triage-next/SKILL.md` (+ `references/` if scoring rubric / branch playbooks grow large). Built via `skill-creator`.
- **EDIT** `~/.claude/skills/topic-to-tickets/SKILL.md` — §8 changes (cite contract, lane + DoR gate in Phase 6, rename Output contract → Audit deliverables).
- **OPTIONAL EDIT** `nr-platform/docs/architecture/ticket-contract/README.md` — cross-ref to automated producers (user decision).
