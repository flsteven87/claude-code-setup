---
name: docs-cleanup
description: >-
  Bold docs-governance housekeeping — purge shipped/dead plans & specs and re-current-ize
  architecture docs so a repo's docs/ describes ONLY current-latest reality. Use whenever the
  user wants to clean up outdated docs or asks "清理過時 docs" / "docs 過時了" / "docs housekeeping" /
  "把已 ship 的 plan/spec 清掉" / "current-latest 清理" / "深度審查 docs", after shipping features when
  plan/spec files pile up, when reviewing docs/ for staleness, when a DOCS_POLICY lifecycle sweep is
  due, or when architecture docs may have drifted from code. Distinct from /latest (auto-memory
  consolidation) and git-state-audit (git tree) — this one owns REPO docs lifecycle. Verifies every
  claim against current code before deleting or asserting; communicates in Traditional Chinese (zh-tw).
---

# docs-cleanup — current-latest docs housekeeping

Repos accumulate doc sediment: plans that shipped but were never deleted, specs describing a design
three iterations behind the code, architecture docs that quietly went wrong when a feature flag
flipped. Agents then waver between the stale version and reality, and quality decays. This skill
walks a repo's `docs/` back to describing **only what is true now and what is genuinely coming next**.

## Governing principle (the whole point)

**Bold. Focus only on the future and the current-latest state. Do not preserve dead scaffolding
"just in case" — git history is the safety net.**

Concretely, this means:
- A shipped plan/spec is **past**, not an asset. Delete it on sight — don't ask "keep it as scratch?".
  That question is the sediment. `git show <sha>:path` revives anything you ever actually need.
- Architecture docs describe **current reality**, with no legacy/back-compat caveats layered on top.
- "Deferred with no committed timeline" ≈ delete candidate. If it's genuinely on the roadmap, keep the
  design (the *noun*) only; kill the plan (the *verb* steps — they'll be stale by the time you build).

This is the stronger, on-sight version of a repo's written delete-after-ship policy. If the repo has
a cleanup precedent commit (e.g. `chore(docs): remove shipped ... per DOCS_POLICY`), it confirms the
governance is live and the user wants it enforced — cite it.

## When to use / when not

**Use** when: the user wants stale docs cleaned; plan/spec files have piled up after a ship streak;
a periodic docs lifecycle sweep is due; someone suspects architecture docs drifted from code; the user
says any trigger phrase in the description.

**Not this skill** for: auto-memory (`MEMORY.md` + topic files) → that's `/latest` or `/handoff`;
git tree / branches / worktrees → `git-state-audit`; writing a *new* doc → just write it.
This skill owns the **repo `docs/` tree** lifecycle. (It will, however, clean up dangling references
that its own deletions leave inside memory files — see Phase 6.)

## Workflow

Run these in order. Phases 1-3 gather ground truth; Phase 4 decides; Phase 5-6 execute; Phase 7 reports.

### Phase 1 — Learn the governance

Read the repo's docs-governance surface if it exists, in this order: `docs/DOCS_POLICY.md`,
`docs/AGENTS.md`, root `AGENTS.md`/`CONTRIBUTING.md`. Extract the **layer model** and **death
conditions**. The near-universal shape:

| Layer | Examples | Death condition |
|---|---|---|
| **L1 durable** | architecture, product, reference, runbooks | system removed |
| **L1 append-only** | **ADRs, audit snapshots** | **NEVER delete** — historical evidence by design |
| **L1↔L2 spec** | design specs | feature fully ships → noun absorbed into architecture, file deleted |
| **L2 ephemeral** | **plans, issue drafts** | **PR merge deletes them** |
| **L3 auto** | graphify output, auto-memory | gitignored / tool-owned; don't hand-edit |

If the repo has **no** governance doc, apply that default model anyway — it's the sane baseline.

### Phase 2 — Inventory

Build the candidate set. For plans and specs, capture **tracked-vs-untracked** and **last-commit date**
(both drive the verdict). One pass:

```bash
for f in docs/superpowers/plans/*.md docs/superpowers/specs/*.md; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    echo "TRACKED  $(git log -1 --format=%cd --date=short -- "$f")  $f"
  else echo "UNTRACKED       $f"; fi
done
```

For architecture / product / reference docs, capture last-commit date + line count (old + large = higher
drift risk). Also read each spec's stated "Lifecycle" / "死亡條件" line — specs are supposed to declare
their own death condition; grep for it.

### Phase 3 — Verify ship-status against git (do NOT assume)

A doc's death condition is only met if the feature **actually shipped**. Confirm each plan/spec against
`git log`, not against memory or the doc's own optimistic claims:

```bash
git log --oneline --all -i --grep='<feature-keyword>'
```

**This is where the skill earns its keep.** A spec may claim "after M2 ships, delete" while M2 (or one of
its sub-decisions) never shipped — `git log -S '<the_symbol_it_introduced>'` returning zero hits is the
tell. Deleting on the doc's say-so would lose an unbuilt-future design. Verify the *specific* symbol/flag/
route the doc introduced, not just the feature name. When a spec is partially shipped, split it: absorb the
shipped part, preserve the unbuilt part (park a one-liner in memory pointing at git history), then delete.

### Phase 4 — Triage

Sort every candidate into exactly one bucket:

- **PURGE** — shipped plan/spec, death condition met. (Most of them, usually.)
- **KEEP** — genuine north-star (multi-milestone terminal-shape spec still being built toward) or a
  deferred design with a real external forcing function (e.g. an upstream API deprecation). Keep the
  *design*, not its plan.
- **CURRENT-IZE** — an L1 architecture/product doc that DRIFTED from code (wrong, stale, or missing a
  shipped feature). These get *fixed*, not deleted.
- **LEAVE** — append-only (ADR/audit), or historical artifacts that are write-protected (e.g. applied
  `migrations/*.sql` — many repos hard-block edits to these) and harmless.

Report the triage before executing so the user sees the shape. Then proceed — don't stop to ask
permission on the PURGE bucket; the principle already authorized it.

### Phase 5 — Purge

Tracked → `git rm <files>` (stages the deletion for one housekeeping commit). Untracked scratch →
`rm <files>`. Keep only the KEEP bucket. An empty `plans/` afterward is correct and honest when there's
no in-flight plan — don't invent one to fill it.

### Phase 6 — Current-ize architecture + clean dangling refs

**Fix drifted docs from CODE, not from the dead specs.** Code is the current truth; the specs were just
rationale. For a broad drift set, fan out read-only verifier agents (one per doc cluster) to pin the
exact drift against code (file:line), then hand the edits to the implementation specialist per the repo's
division-of-labor rule, and verify the result yourself. Common drift classes: a predicate/formula the code
changed; a table missing a newly-shipped row; framing that a flag-flip inverted (shadow→active); renamed
paths; a UI section count that changed.

**Then clean the dangling references your deletions created** — this is not optional, a broken pointer is
the same sediment you just removed:
- grep memory files + `docs/` + `AGENTS.md` for every deleted basename; fix or drop each hit.
- **Safety check:** grep `backend/ frontend/ .github/` for the deleted paths — some repos import doc
  markdown into tests (contract-testing prose against behavior). A real import means the deletion breaks
  the build; a mere `-- Spec: <path>` comment in a write-protected migration is harmless, leave it.

### Phase 7 — Report + commit

Report the delta in the user's fixed micro-block form (**淨變化 / 在哪看 / 沒包含**). Then land the whole
pass — purge + current-ization — as **one** housekeeping commit (mirror any precedent commit's message
shape). Push per the repo's git-automation rules. Don't split the purge from the fixes; they're one unit.

## Guardrails

- **Never delete ADRs or audit snapshots.** They're append-only historical evidence — that's their job.
  A reversed ADR gets a *superseding* ADR, not a deletion.
- **Verify before you delete or assert.** Trust neither the doc's own claims nor stale recalled memory —
  read current code. Recalled file:line citations may be months old.
- **Code is the current-truth source for current-izing.** Don't fold a stale spec's prose into an
  architecture doc verbatim; describe what the code does now.
- **Don't touch write-protected historical files** (applied `migrations/*.sql`); leave their doc-comment
  references — they're harmless and often un-editable by policy.
- **The "keep as scratch?" question is banned.** The principle is the answer: delete. Surface a genuine
  tension (e.g. "this deferred design has no timeline — kill it too?") once, briefly, then move on.

## Communication

Traditional Chinese (zh-tw), decision-shaped, recommendation-first. Technical tokens (SHA, file paths,
enum values, commands) stay in English. Lead the final report with what is now true, not what you did.
The delta micro-block is the deliverable; the triage table is the audit trail.
