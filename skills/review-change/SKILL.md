---
name: review-change
description: Use when the user says /review-change or wants a findings-first review of current staged, unstaged, or targeted code changes. Defaults to a TERSE one-line-per-finding fix list, not a narrative report. Full zh-tw report only when the user explicitly asks for "詳細" / "deep" / "full report".
---

# Review Change

Find blockers in the diff. Output a fix list, not a narrative.

This skill exists to surface bugs and convention violations in changed code so the caller can fix them — not to produce essays. When called as a sub-skill (e.g. from `/close-PR`), the output feeds the parent's fix loop directly. Long reports break parent pipelines.

## Scope (hard rule)

1. Establish file list: `git diff origin/main...HEAD --name-only` (NOT `git diff --name-only`, which leaks local edits) when the parent passes a PR-style branch context. Otherwise `git diff --name-only`.
2. Review ONLY those files.
3. If you notice issues in out-of-scope files, surface them as a one-liner labeled `[OOS]` — never silently fix.
4. Override only when the user explicitly says "review everything" or names files directly.

Aligns with global Scope Discipline rule.

## Review focus (priority order)

Walk in order. Stop scanning when no signal remains; don't fabricate findings to fill dimensions.

### 🔴 P1 — Project conventions (the original intent of this skill)

These are the violations that actually break the codebase. Surface every instance.

- **CLAUDE.md Absolute Prohibitions**: bypassed 4-Layer Architecture (DB calls in endpoints, business logic in repositories), `result.data` accessed directly in repos, `any` in TS critical paths, `React.createElement`, `React.FC`, `require()` imports, bare `except:`, missing `raise ... from e`, barrel imports from icon/component libraries, sequential `await` on independent ops, god components >1000 lines, `FORWARDED_ALLOW_IPS=*`, `FOR ALL TO public USING (true)` RLS, missing `SET search_path = 'public'` on Postgres functions, naive `datetime.now()` in expiry/boundary code.
- **Single Elegant Version**: development-stage adjectives (`enhanced_`, `_v2`, `_old`), parallel-version files, deprecation-shim re-exports, defensive coding for impossible internal states.
- **4-Layer boundaries**: API → Service → Repository. Endpoints calling DB directly. Services importing HTTP types. Repositories with business logic.
- **Async discipline (Python)**: `async def` doing blocking I/O. Should-be-parallel awaits running sequentially.
- **Pydantic V2 only**: `@validator` / `@root_validator` / `class Config:` / `.dict()` / `.json()` — flag any V1 syntax.
- **Repository pattern**: missing `_handle_supabase_result()` / `_build_model()`, direct `result.data[0]` indexing.
- **Project-specific naming**: file name ≠ primary export; class suffix mismatch (Handler/Processor/Service); snake_case vs camelCase mixing.

### 🟡 P2 — Bugs and silent behavior changes

- Silent behavior changes hidden in "refactor" hunks (cache key shape, response payload shape, default values).
- Security: IDOR, unvalidated input at API boundary, secrets in logs, missing auth gate on new endpoint.
- Schema/contract mismatch (field renamed in one place, not the call site).
- Test fixture drift from production wiring.

### 🟢 P3 — Opt-in only

Only walk these when the caller's args mention them, OR the user invoked /review-change directly with "詳細" / "deep" / "full review":

- DRY heuristics, stylistic micro-cleanups, comment polish, naming bikeshedding, performance micro-optimizations, coverage-gap heuristics.

Default behavior: skip P3. Three similar lines is fine; over-DRY-ing is more harmful than mild duplication.

## Action policy

- **Fix-in-place** for mechanical issues only when caller is the user directly: lint errors, unused imports, missing exception chaining, format drift. Report what was fixed.
- **Flag-only** for everything else, including all P1/P2 findings — let the caller decide.
- When called as a sub-skill (parent prompt mentions "PR scope" / "fix list" / "feed parent" / "close-PR"), default to **flag-only** even for mechanical issues — the parent's fix loop owns the writes.
- Never touch files outside the `git diff` set.

## Output contract

**Default (terse, sub-skill safe).** One line per finding. No section headers. No narrative. No zh-tw report ceremony.

```
[CRITICAL] file:line — concrete risk · fix direction
[HIGH] file:line — concrete risk · fix direction
[MEDIUM] file:line — concrete risk · fix direction
[LOW] file:line — concrete risk · (skip if not mechanical)
[OOS] file:line — out-of-scope observation, not fixed
```

If no findings: output literally `no findings` on a single line.

If mechanical fixes were applied: prepend `[FIXED] file:line — what changed` lines above the findings list.

**Verbose mode (only when user explicitly invokes /review-change with "詳細" / "deep" / "full report" in args).** Add a brief zh-tw summary BELOW the fix list:

```
## 摘要
- 主要風險：<one sentence>
- 已修：<count> 個 mechanical fix
- 殘餘風險：<one sentence>
```

That's it. No 5-section ceremony. No "Findings / Fixed in place / Open questions / Verification results / Residual risk" template — that template was the source of mid-pipeline interruptions in `/close-PR`.

## Verification

When called as a sub-skill, **skip running CI commands** — the parent's verify gate (Phase 5 in `/close-PR`) owns that step. Running `ruff` / `pytest` here duplicates work and slows the pipeline.

When invoked directly by the user, run scoped commands matching the changed paths (`uv run ruff check <changed.py>`, `npm run lint` in affected app dir). Map each changed source file to its specific test file; do NOT broaden to parent test directories. If lint or in-scope tests fail and the failure is mechanical, fix-in-place and re-verify.

## Rules

- If there are no findings, say `no findings` and stop. Do not invent issues to look thorough.
- Each finding is an evidence-backed claim: file path, line number, concrete risk, minimal fix direction. No style preferences.
- One line per finding. Multi-line explanations belong in PR review comments, not in this skill's output.
- Default is terse. Verbose is the exception, not the norm.
- Sub-skill mode (parent calling): treat your output as a machine-readable fix list — the parent will surface what's needed to the user.
