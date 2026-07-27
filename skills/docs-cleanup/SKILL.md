---
name: docs-cleanup
description: "Purge doc sediment from a repo's docs/ — delete shipped plans and specs, re-current-ize drifted architecture docs — so the tree describes only what is true now and what is genuinely coming next. Use when the user wants stale docs cleaned, plan/spec files have piled up after shipping, or architecture docs may have drifted from code."
argument-hint: "[docs subtree or scope]"
---

# docs-cleanup

Repos accumulate **sediment**: plans that shipped but were never deleted, specs describing a design
three iterations behind the code, architecture docs that quietly went wrong when a flag flipped.
Agents then waver between the stale version and reality. This skill walks a repo's `docs/` back to
describing only current-latest truth and genuinely-coming-next work.

## Governing principle

**Git history is the safety net, so dead scaffolding gets deleted on sight.**

- A shipped plan or spec is past, not an asset. `git show <sha>:path` revives anything you ever
  actually need — which is what makes deletion the cheap move and「留著當 scratch？」the sediment.
- Architecture docs describe current reality, standing on their own without legacy caveats layered
  on top.
- Deferred with no committed timeline ≈ delete candidate. Genuinely on the roadmap → keep the design
  (the *noun*); the plan (the *verb* steps) will be stale by the time you build it.

A repo cleanup precedent commit (`chore(docs): remove shipped ... per DOCS_POLICY`) confirms the
governance is live — cite it.

This skill owns the repo `docs/` tree. `MEMORY.md` and topic files belong to `/latest` and
`/handoff`; branches and worktrees belong to `git-converge-main`.

## Phase 1 — Learn the governance

Read, in order, whichever exist: `docs/DOCS_POLICY.md`, `docs/AGENTS.md`, root `AGENTS.md`,
`CONTRIBUTING.md`. Extract the layer model and death conditions. The near-universal shape, which is
also the default when a repo has no governance doc:

| Layer | Examples | Death condition |
|---|---|---|
| L1 durable | architecture, product, reference, runbooks | system removed |
| L1 append-only | **ADRs, audit snapshots** | never deleted — historical evidence by design; a reversed ADR gets a *superseding* ADR |
| L1↔L2 spec | design specs | feature fully ships → noun absorbed into architecture, file deleted |
| L2 ephemeral | plans, issue drafts | PR merge deletes them |
| L3 auto | generated indexes, auto-memory | tool-owned; leave alone |

**Complete when** the layer model and each layer's death condition are stated, sourced from the repo
or explicitly from the default.

## Phase 2 — Inventory

For plans and specs, capture tracked-vs-untracked and last-commit date — both drive the verdict:

```bash
for f in docs/plans/*.md docs/specs/*.md docs/*/plans/*.md docs/*/specs/*.md; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    echo "TRACKED  $(git log -1 --format=%cd --date=short -- "$f")  $f"
  else echo "UNTRACKED       $f"; fi
done
```

For architecture / product / reference docs, capture last-commit date and line count — old and large
means higher drift risk. Specs are supposed to declare their own death condition; grep each for its
「Lifecycle」/「死亡條件」 line.

**Complete when** every file under the docs tree appears exactly once in the inventory with its
tracked state and date.

## Phase 3 — Verify ship-status against git

A death condition is met only if the feature **actually shipped** — confirmed against `git log`,
never against memory or the doc's own optimistic claim.

```bash
git log --oneline --all -i --grep='<feature-keyword>'
git log -S '<the_symbol_the_doc_introduced>'
```

**This is where the skill earns its keep.** A spec may say「M2 ships → delete」while M2, or one of its
sub-decisions, never shipped; `git log -S` returning zero hits on the specific symbol, flag, or route
the doc introduced is the tell. Deleting on the doc's say-so loses an unbuilt-future design.

Partially shipped → split it: absorb the shipped part into architecture, park a one-liner in memory
pointing at git history for the unbuilt part, then delete the file.

**Complete when** every purge candidate has a git citation — a commit proving the ship, or a
zero-hit `-S` search proving it did not.

## Phase 4 — Triage

Every candidate lands in exactly one bucket:

- **PURGE** — shipped plan/spec, death condition met and git-verified. Usually most of them.
- **KEEP** — a genuine north-star spec still being built toward, or a deferred design with a real
  external forcing function (an upstream API deprecation). Keep the design, not its plan.
- **CURRENT-IZE** — an L1 doc that drifted from code: wrong, stale, or missing a shipped feature.
  These get fixed.
- **LEAVE** — append-only (ADR / audit), or write-protected historical artifacts such as applied
  `migrations/*.sql`.

Report the triage table so the user sees the shape, then execute. The PURGE bucket is already
authorized by the governing principle; a genuine tension (a deferred design with no timeline) gets
surfaced once, briefly, and then decided.

**Complete when** every inventory item sits in exactly one bucket and the table has been shown.

## Phase 5 — Purge

Tracked → `git rm <files>`, staging the deletion for one housekeeping commit. Untracked scratch →
`rm <files>`. An empty `plans/` afterward is the correct and honest outcome when nothing is in
flight.

**Complete when** the PURGE bucket is empty and `git status` shows exactly those deletions.

## Phase 6 — Current-ize and clean dangling refs

Fix drifted docs **from code**, which is the current truth; the dead specs were only rationale. For a
broad drift set, fan out read-only verifiers (one per doc cluster) to pin each drift at `file:line`,
hand the edits to the implementation specialist per CLAUDE.md Part 3, and verify the result yourself.
Common drift classes: a predicate or formula the code changed; a table missing a newly-shipped row;
framing a flag-flip inverted (shadow→active); renamed paths; a changed section count.

Then clean the references your deletions just broke — a dangling pointer is the same sediment you
removed:

- grep memory files, `docs/`, and `AGENTS.md` for every deleted basename; fix or drop each hit;
- grep `backend/ frontend/ .github/` for the deleted paths. Some repos import doc markdown into
  tests (contract-testing prose against behavior), where a deletion breaks the build. A bare
  `-- Spec: <path>` comment inside a write-protected migration is harmless and stays.

**Complete when** every deleted basename returns zero live references, and every CURRENT-IZE doc's
changed claims are each backed by a `file:line` in current code.

## Phase 7 — Report and commit

Report the delta in the fixed micro-block form（**淨變化 / 在哪看 / 沒包含**）, leading with what is
now true. Land purge and current-ization as **one** housekeeping commit — they are one unit —
mirroring any precedent commit's message shape. Push per CLAUDE.md Git Automation.

**Complete when** the commit exists, the push resolved per policy, and the micro-block names both
what changed and what was deliberately left.

## Communication

zh-tw, decision-shaped, recommendation-first. Technical tokens (SHA, paths, enum values, commands)
stay English. The delta micro-block is the deliverable; the triage table is the audit trail.
