# triage-next Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `anthropic-skills:skill-creator` to author the new skill (Tasks 1–3, 6) and direct `Edit` for the topic-to-tickets change (Task 4). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `triage-next` skill (autonomous post-`/latest` board-clearing → contract/dispatch/close router) and wire `topic-to-tickets` to the existing ticket-contract SSOT.

**Architecture:** New user-level orchestrator skill that selects by B>C>A, classifies the next actionable unit into 3 branches, and composes existing skills (`reverse-thinking`, `topic-to-tickets`, `code-review`, `narrate-glance`). Single content SSOT for the contract = `nr-platform/docs/architecture/ticket-contract/`.

**Tech Stack:** Markdown skills under `~/.claude/skills/`; Skill-tool composition; Linear/gh/git as the board signals. No runtime code, no pytest.

**Content spec (DRY):** the full design lives in [`DESIGN.md`](DESIGN.md). Each task references the section that defines its content rather than re-pasting it. "Author per §X" means "write the SKILL content implementing DESIGN.md section X," not a placeholder.

**Verification model (skill-adapted):** instead of failing-test cycles, each task verifies by (a) structural check — required sections/frontmatter present; (b) trigger check — description fires on intended phrases; (c) a dry-run against the *current real board* (post-`/latest`: own open PRs = 0, NEX-1069 R3.4 = ready contract/Backlog, NEX-1035 = stalled In-Progress, NEX-1067 = ready contract) to confirm sensible pick + route.

**Commits:** `~/.claude/` version-control status is unconfirmed. Commit steps are marked optional — run them only if `~/.claude` is a git repo (`git -C ~/.claude rev-parse --git-dir` succeeds); otherwise the Write itself is the checkpoint.

---

### Task 1: Scaffold triage-next skill + frontmatter/triggers

**Files:**
- Create: `~/.claude/skills/triage-next/SKILL.md`
- Reference: `~/.claude/skills/triage-next/DESIGN.md` (already written)
- Decide: whether to split detail into `~/.claude/skills/triage-next/references/` (do so if SKILL.md would exceed ~180 lines, per skill-creator guidance)

- [ ] **Step 1: Invoke skill-creator to scaffold**

Use `anthropic-skills:skill-creator` to create skill `triage-next`. It owns dir layout + frontmatter validation. Point it at `DESIGN.md` as the content source.

- [ ] **Step 2: Write the frontmatter exactly**

```markdown
---
name: triage-next
description: Use after /latest to autonomously pick the single highest-value noise-reducing topic off the board, ramp on it, and drive it to one of three terminal states — spec a contract ticket, confirm an already-ready contract for dispatch, or deep-review partial work for closing. Triggers on '/triage-next', '清板', '降噪選題', '下一步收什麼', '挑一題收尾', '接下來收哪個', 'what to close next', or right after /latest when the user wants the next move chosen and driven automatically. Selects by open-loop reduction > momentum > delegatability. Cites the ticket-contract SSOT; ends with a /narrate-glance report. NOT /strategic-next (that is big-bet leverage analysis) — this is autonomous board-clearing.
---
```

- [ ] **Step 3: Verify frontmatter + triggering**

Run: `head -5 ~/.claude/skills/triage-next/SKILL.md` and confirm `name: triage-next` matches the dir; description contains both `/triage-next` and zh-tw trigger phrases (`清板`, `降噪選題`).
Expected: name/dir match; trigger phrases present; explicit NOT-strategic-next disambiguation present.

- [ ] **Step 4 (optional): Commit**

```bash
git -C ~/.claude rev-parse --git-dir && git -C ~/.claude add skills/triage-next/ && git -C ~/.claude commit -m "feat(skill): scaffold triage-next"
```

---

### Task 2: Author Stage 1 — survey + B>C>A rubric + classifier

**Files:**
- Modify: `~/.claude/skills/triage-next/SKILL.md` (Stage 1 section)
- Or create: `~/.claude/skills/triage-next/references/selection-rubric.md` (if splitting)

- [ ] **Step 1: Author the Stage 1 flow per DESIGN §4**

Must contain, concretely:
- Candidate pool: read freshly-synced `MEMORY.md` structure as topic skeleton; verify with `gh pr list`, Linear started/Todo, `git branch`.
- Selection: **ordered criteria, NOT numeric weights** — sort by B, tie-break C, then A. Enumerate the per-axis signals from §4.2 verbatim (open-loop / momentum / delegatability lists). Include the explicit guard: "no magic-number thresholds (theater); show which signals fired."
- Classifier decision tree from §4.3 (code-exists? → ③ ; else ready-contract? → ② ; else ① ), operating on the **next actionable unit**.
- Stage 1 GATE output spec from §4.4 (landscape + pick + next unit + proposed branch + why-it-won + user may override).

- [ ] **Step 2: Verify structural completeness**

Run: `grep -niE "B>C>A|next actionable unit|fired|override|magic" ~/.claude/skills/triage-next/SKILL.md` (or the references file).
Expected: all four sub-parts present; the "no magic-number" guard present; classifier tree present.

- [ ] **Step 3: Dry-run the selector against the current board**

Reason through Stage 1 on the known post-`/latest` state. Expected sensible output, e.g.: landscape lists NEX-1034 R3 chain, NEX-1035, NEX-860, globalization cluster; pick surfaces a high-B item; classifier routes NEX-1069 (ready contract) → ②, a stalled In-Progress → ③, an unspecced High → ①.
Expected: pick + route are defensible from fired signals; no black-box ranking.

- [ ] **Step 4 (optional): Commit** (same conditional pattern as Task 1 Step 4)

---

### Task 3: Author Stage 2 branches + composition + escape hatch + report

**Files:**
- Modify: `~/.claude/skills/triage-next/SKILL.md` (Stage 2 section)
- Or create: `~/.claude/skills/triage-next/references/branch-playbooks.md` (if splitting)

- [ ] **Step 1: Author the three branches per DESIGN §5**

- ① TRIAGE: RAMP → invoke `reverse-thinking` (distill) → apply `karpathy-guidelines` lens → invoke `topic-to-tickets` (feeding pre-confirmed scope + RAMP cites + north star so it fast-forwards its Phase 1/2 + audit Part A). Terminal: contract ticket(s), ready to hand off (user dispatches).
- ② READY: run Definition of Ready (cite `docs/architecture/ticket-contract/README.md`); pass → signal "可直接交 Joi/TARS", NO mutation; fail → downgrade to ① transparently.
- ③ PARTIAL: invoke `/code-review` (deep) on existing code/PR + finishing recommendations, NO mutation; optionally suggest folding into a ① finishing contract.

- [ ] **Step 2: Author composition seams (§12), escape hatch (§9), report (§10), edge cases (§13)**

- Composition: same-context Skill-tool invocation; Branch ① inherits topic-to-tickets Phase 5 mutation gate; honest Codex fallback.
- Escape hatch: interrupt only on `human_decision_needed: yes` categories (product/business/credential/irreversible-data/security-posture).
- Report: every branch ends by invoking `narrate-glance` — ≤50 lines, 5 sentences + diagram, dual-axis (solved/remaining).
- Edge cases: clean board; mixed-state chain → single next unit; Stage 1 override; Codex unavailable.

- [ ] **Step 3: Verify referenced skills + gates**

Run: `grep -niE "reverse-thinking|topic-to-tickets|code-review|narrate-glance|karpathy|human_decision_needed" ~/.claude/skills/triage-next/SKILL.md` (or references file).
Expected: all 5 composed skills named with correct invocation; both gates (Stage 1 + inherited mutation) described; escape-hatch 5 categories present; narrate-glance terminal on all three branches.

- [ ] **Step 4: Verify SKILL.md size / split decision**

Run: `wc -l ~/.claude/skills/triage-next/SKILL.md`
Expected: if > ~180 lines, detail moved to `references/`; SKILL.md stays a lean orchestration spine with pointers.

- [ ] **Step 5 (optional): Commit**

---

### Task 4: Wire topic-to-tickets to the contract SSOT

**Files:**
- Modify: `~/.claude/skills/topic-to-tickets/SKILL.md`

- [ ] **Step 1: Rename the colliding section**

Change the heading `## Output contract` (SKILL.md ~L22) → `## Audit deliverables`. Update any in-file references to that phrase. (It lists audit artifacts, not a ticket contract.)

- [ ] **Step 2: Wire Phase 6 to the ticket-contract policy**

In Phase 6 (Linear ticket mutation), add: produce each ticket per `docs/architecture/ticket-contract/ticket-template.md` (compact for express/standard, full for heavy); assign a **lane**; **gate on the README Definition of Ready** before mutating; cite `docs/architecture/ticket-contract/` as the SSOT (do not duplicate the schema into the skill).

- [ ] **Step 3: Add a citation pointer near the Output-contract/Workflow top**

Add one line: "Tickets MUST conform to the ticket-contract SSOT: `docs/architecture/ticket-contract/` (template + Definition of Ready)."

- [ ] **Step 4: Verify the edit**

Run: `grep -niE "Audit deliverables|ticket-contract|Definition of Ready|lane" ~/.claude/skills/topic-to-tickets/SKILL.md`
Expected: no remaining `## Output contract` heading; citation path present; DoR gate + lane referenced in Phase 6.

- [ ] **Step 5: Confirm no trigger regression**

Run: `head -5 ~/.claude/skills/topic-to-tickets/SKILL.md`
Expected: frontmatter `name`/`description` unchanged (the edit is body-only; triggering must not shift).

- [ ] **Step 6 (optional): Commit**

---

### Task 5 (OPTIONAL — pending user decision): ticket-contract README cross-ref

**Files:**
- Modify: `nr-platform/docs/architecture/ticket-contract/README.md`

- [ ] **Step 1: Add a cross-ref line** (only if user opts in, DESIGN §14)

Under "Who this is for" or "Claude Code drafting flow", add: "Automated producers: the `/triage-next` skill (Branch ①) and `topic-to-tickets` draft tickets against this policy."

- [ ] **Step 2: Verify DOCS_POLICY compliance**

This edit is to a repo doc → governed by DOCS_POLICY. Confirm: it modifies an existing L1 architecture doc (no new SSOT, no Lifecycle line needed for non-design-spec), standard markdown links only, no wikilinks.
Run: `grep -nE "\[\[|\!\[\[" nr-platform/docs/architecture/ticket-contract/README.md` → Expected: no matches.

- [ ] **Step 3: Commit to nr-platform** (this IS the project repo — follow project git rules; branch off main, do not commit to main directly)

---

### Task 6: Validate triage-next end-to-end

**Files:**
- Reference: `~/.claude/skills/triage-next/SKILL.md`, `DESIGN.md`

- [ ] **Step 1: Run skill-creator eval / triggering benchmark**

Use skill-creator's eval to confirm the description triggers on the intended phrases and does NOT collide with `/strategic-next` or `/latest`.
Expected: high-confidence trigger on `/triage-next` + zh-tw phrases; clean separation from strategic-next.

- [ ] **Step 2: Full dry-run against the current board**

Walk the whole pipeline once on the real post-`/latest` state without mutating anything: Stage 1 survey → pick → classify → (simulate) the chosen branch → confirm it would end at a narrate-glance report and the correct gate.
Expected: a coherent run that picks a real high-B topic, routes correctly, and stops at the Stage 1 gate (and, for ①, would stop again at the mutation gate).

- [ ] **Step 3: Read the Hermes audit for late lessons**

Read `nr-platform/docs/audits/2026-05-22-hermes-5day-audit.md`; fold any concrete ticket-quality→automation lessons into the Branch ① contract-drafting notes or the DoR emphasis.
Expected: any high-value lesson captured or explicitly deemed already-covered.

- [ ] **Step 4: Resolve the open questions (DESIGN §14) with the user**

Confirm: final name; express-lane Codex scaling; whether `/latest` auto-suggests this skill; whether Task 5 cross-ref ships.

- [ ] **Step 5 (optional): Final commit**

---

## Self-Review

- **Spec coverage:** DESIGN §1–§13 each map to a task — §2/§4 → Task 2; §5/§9/§10/§12/§13 → Task 3; §6/§7/§8 → Task 4 (+§6 cited in Task 3 ② ); §11 strategic-next retirement = explicitly deferred follow-up (DESIGN §11, not v1) — no task, by design; §14 open questions → Task 6 Step 4. Covered.
- **Placeholder scan:** "Author per §X" references concrete written sections in DESIGN.md, not TBDs. Verification steps are runnable greps/dry-runs. No vague "add error handling".
- **Type/name consistency:** skill names used consistently (`triage-next`, `topic-to-tickets`, `reverse-thinking`, `code-review`, `narrate-glance`, `karpathy-guidelines`); section rename (`Output contract`→`Audit deliverables`) applied in Task 4 and referenced nowhere else as the old name.
