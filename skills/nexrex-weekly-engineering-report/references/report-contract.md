# Weekly Report Contract

## Evidence hierarchy

1. Linear issue description and relations: originating symptom, investigation, decisions, status.
2. Git first-parent commit and diff: code or configuration actually merged to `main`.
3. PR attachment/body and recorded verification: intended scope and existing test evidence.
4. Current source and targeted checks: resolve discrepancies only.

Do not use commit titles alone when a ticket or diff is available.

Reconcile PR identifiers from Git references and Linear attachments. A count of PR numbers found in commit messages is a lower bound, not the total delivery count.

## Claim rules

- Separate `problem`, `root cause`, `merged change`, and `remaining scope`.
- Use `confirmed` only when the issue or source contains evidence, not a hypothesis.
- Treat an issue marked `Done` as workflow state, not proof of runtime recovery.
- Treat a PR attachment as traceability, not proof that all ticket symptoms were implemented.
- When one ticket mentions multiple symptoms but the attached diff fixes one, name the fixed symptom and mark the others `未拆分` or `待確認`.
- When an incident leads to an architecture program, show the chain in one main item instead of listing every child ticket separately.
- State backlog rollout gates explicitly; never describe an in-progress umbrella as closed.

## Five-item compression

Choose up to five coherent items, not five individual commits. Use five when the evidence supports five; otherwise use fewer and never inflate a minor fix. Use this shape:

1. `NEX / PR references`
2. Neutral topic title
3. Two to four factual sentences covering problem, root cause/change, and status

Move one-line fixes, isolated refactors, CI cleanup, documentation, and small performance changes to the right-side `小改動` list.

## Language

Use neutral verbs: `新增`, `修正`, `移除`, `遷移`, `限制`, `保留`, `拆分`, `驗證`.

Avoid ratings and promotional language, including:

- 高產出、高影響、亮眼、完整、成熟、穩健
- 做得很好、工程品質良好、值得肯定
- 顯著提升 unless a measured before/after value is cited
- 成功解決 unless the reported user outcome was verified

Counts describe scope only. Never use PR, commit, line, or test counts as a productivity score. Label lower-bound counts precisely, for example `Git-referenced PRs`, until all PR sources are reconciled.

## Validation wording

- Prefer verification recorded on the relevant ticket or PR.
- If local checks are run, list exact pass/fail counts and environmental blockers.
- Do not collapse a partially failing gate into `tests passed`.
- Do not attribute broad failures to the contributor without a failing assertion tied to an in-scope diff.

## One-page HTML layout

- Top: date/source line and at most three scope counts.
- Left: up to five numbered main items; default to five when available.
- Right: `小改動`, then `未完成／待確認`; add validation only if it changes interpretation.
- Keep status text visible without hover or interaction.
- Use theme variables and responsive stacking through the `visualize` skill.
- Render at the intended desktop viewport and inspect the result. Complete only when it is one page,
  has no clipped or overlapping text, no unintended horizontal overflow, and all status text remains
  legible. Also inspect the responsive stacked layout when it is part of the requested deliverable.
- Do not add verdict, score, rating, praise, or decorative qualitative badges.

## Privacy

Keep NEX and PR identifiers. Remove personal names from support tickets when not necessary, and never include raw email addresses, Firebase UIDs, request IDs, tokens, or private attachment URLs.
