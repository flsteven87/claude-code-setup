---
name: ending
description: Use when implementation is done and you want to take finished code from "works" to "shipped + documented". Triggers on '/ending', 'wrap this up', 'ship the changes', '收尾', '結束這個'.
---

# Ending — Finished Code → Shipped (Highly Automated)

```
review-change → simplify → verify → review-and-commit → handoff
```

**User-facing output: zh-tw** (per CLAUDE.md). SKILL structure stays English.

## What this skill IS — and is NOT

IS: a pipeline runner that invokes each named sub-skill via the `Skill` tool, in order, autonomously. The agent decides nothing the sub-skills can decide.

IS NOT: a place to add new analysis, opinions, or ad-hoc checks. Anything not done by the four sub-skills + the verification gate does not belong here.

## Cardinal rule: each phase MUST be a `Skill` tool call

**The only proof a phase ran is a `Skill <name>` tool call this turn.** Manual git-diff reading is NOT a substitute for `/review-change`. Manual MEMORY edit is NOT a substitute for `/handoff`. `gh pr merge` alone is NOT a substitute for `/review-and-commit`.

If you finish what feels like a "phase" without making a `Skill` tool call, you skipped the phase. Go back.

## Default: auto-fix, do not ask

The user invoking `/ending` is consent for autonomous execution including:

- **Mechanical fixes**: lint errors, unused imports, naming inconsistencies, obvious DRY violations, trivial code-quality tweaks → fix in place inside `/simplify` (or `/review-change` per its own policy).
- **Best-practice precision drift** found in Verify → fix in place inside Phase 3, do NOT defer.
- **Stale fixtures / tests inside diff scope** → update them.
- **CHANGELOG / MEMORY entries** missing → add them.

Only stop and ask the user when one of the **objective triggers** below fires.

## Mode detection

Detect at Phase 1 start whether HEAD's tip commit is your own work in this session:

- **Author mode** — you wrote the code. Auto-fix bias applies fully. `/simplify` may rewrite anything in diff scope. `/review-and-commit` produces the actual commit.
- **Gatekeeper mode** — HEAD is someone else's PR you are merging, OR HEAD is already merged on main. Scope Discipline still applies: do NOT mutate the merged diff. Auto-fix moves into a **post-merge follow-up commit** (existing repo precedent: `docs(changelog): ...`). `/review-and-commit` produces that follow-up commit. `/simplify` may run as no-op if nothing in scope is yours to change — let the skill decide, not you.

Do NOT decide "skip this phase" from mode alone. Run every phase; let the sub-skill's body handle the no-op when applicable.

## Phases

1. **Review** — `Skill review-change`. Findings stay as internal context. Mechanical fixes the skill applies in-place are kept.
2. **Simplify** — `Skill simplify`. Strictly within Phase 1's diff scope. Auto-applies refactors.
3. **Verify** — deep regression + best-practice gate. Run BEFORE commit:
   - Lint + type-check + relevant test suite (project commands from `CLAUDE.md`).
   - Re-read the diff and answer truthfully:
     1. Could this change break any currently-passing path?
     2. Does each line follow project best practice — naming, layering, no `any`, no defensive boilerplate, no over-abstraction, no scope creep?
   - "Not confident" on either → fix it now inside Phase 3. Do NOT defer.
4. **Commit** — `Skill review-and-commit`. In gatekeeper mode this produces the post-merge follow-up commit. Push only on a branch the user previously authorized for this stream.
5. **Handoff** — `Skill handoff`. Update MEMORY.md (active work, deferred findings, gotchas).

## Stop only when (objective triggers)

Hard stops — block and ask the user:

- A sub-skill blocks, errors, or explicitly requests user input.
- Phase 1 surfaces a 🔴 — security issue, broken invariant, failing test in diff scope, data-loss risk, RLS hole.
- Phase 3 verification fails AND root cause is not within current diff scope (chronic main red is NOT a stop trigger — note it in the report and ship).
- About to push to a shared branch without prior authorization for this stream.
- About to violate a 🔴 rule declared in project `CLAUDE.md`.
- Mode-detection ambiguous (uncommitted changes mixed with someone else's commit on HEAD).

When stopping, print: current phase, the specific trigger, and the minimal question needed to unblock. No multi-option menus. Do NOT stop on 🟡 — fix it.

## Self-check before completion report

Before writing the user-facing report, count your `Skill` tool calls this turn. Required: `review-change`, `simplify`, `review-and-commit`, `handoff` — four invocations. If count < 4, the report is forbidden until you go back and run the missing skills.

## Completion report (zh-tw, executive tone)

Plain language, essence only. No file:line clutter unless decision-weight.

Required sections (all short):

- **改動精髓** — 1–2 句。為什麼這次變動值得收尾，本質是什麼。
- **品質確認** — 必須引用 `/review-change` 的 finding 數量與最高嚴重度，以及 `/simplify` 實際動到幾個檔案。講不出來代表 skill 沒跑，回去補。
- **Commit + 推送狀態** — `<hash>` `<subject>`，是否已 push、推到哪個 branch。
- **Handoff 寫入** — MEMORY 多了哪些可在未來節省時間的事實 / 待辦。
- **接下來自然的一步**（可省略）— 只在這次變動明顯帶出下一個小工作時才寫。

Avoid: phase-transition framing ("Phase X complete"), full lint output, internal jargon, justifications for not running a skill.

## Failure

On any phase failure: stop, print which phase, the failing artifact, and the minimal unblocking question. Do not auto-retry. Do not silently degrade to manual.
