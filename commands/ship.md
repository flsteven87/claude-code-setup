---
description: Solo / main-based ship pipeline — simplify (Codex) → review (Codex) → commit & push to origin/main. Express lane for small + clear diffs.
disable-model-invocation: true
---

# /ship — working tree → `origin/main`

Drive a finalized change to `origin/main`. Normal entry is after `/mattpocock-skills:implement`
finishes a batch, which leaves the repo **pre-committed** (clean tree, N commits ahead of
`origin/main`); an uncommitted working tree is the other accepted shape.

This command orchestrates; implementation and review work go to Codex per CLAUDE.md Part 3.

`/ship` is user-invoked only. The invocation is the push authorization, so the pipeline can reach
`git push` without a second prompt — that only holds while a human is the one typing it.

| Lane | Stages | When |
|---|---|---|
| **Express** | 1 → 1.5 → 5 → 6 → 6.5 → 7 | Small, clear diff with no load-bearing code semantics |
| **Full** | + 2 → 3 → 4 → 4.5 | Default for everything else |

---

## 1. Pre-flight

Compute the **ship surface** — the aggregate change going to `origin/main`:

```bash
git status --short
git rev-list --left-right --count origin/main...HEAD
```

| Observed | Baseline | Diff |
|---|---|---|
| `git status --short` non-empty | `HEAD` | `git diff HEAD` |
| Clean tree, `origin/main..HEAD` non-empty | `origin/main` | `git diff origin/main..HEAD` |
| Both empty | — | abort: `Nothing to ship.` |

Show one screen: branch + ahead/behind, `git diff --stat <baseline>`, and commit subjects when
pre-committed. Unrelated staged changes mixed in → ask whether to ship together or split.

**Complete when** the baseline, the diff command, and the file list are fixed and echoed to the
user, and every entry in `git status --short` is accounted for as either in-surface or unrelated.

## 1.5. Lane decision

Express requires **all six** to hold:

- **No load-bearing code.** Impact is local and textual: prose, `.gitignore`, `.editorconfig`,
  `.env.example`, comments, docstrings, pure renames — plus styling-layer swaps (Tailwind class
  strings, `oklch(...)` values, colour/spacing tokens) where the function-level contract is
  unchanged and the diff is a runtime no-op except for appearance.
- **No security-sensitive surface.** Auth, authorization, RLS, payments, webhook receivers, secrets,
  CORS/CSP — blast radius outranks diff size here.
- **No schema.** `migrations/*.sql`, Pydantic field changes, GraphQL schema, OpenAPI spec.
- **Small in meaningful terms.** ≤ ~200 net lines and ≤ ~10 files of *meaningful* change.
  Mechanical mass edits don't count against this — a 600k-line `git rm --cached` for a `.gitignore`
  policy fix is still express-eligible.
- **Single coherent concept.** One commit, or N commits already chained deliberately.
- **Designed in this session**, so the user holds full context. A worktree reopened from last week
  goes full lane.

Classify:

| Class | Condition | Action |
|---|---|---|
| **clean-express** | every criterion a clear pass | announce lane + per-criterion reasoning, proceed; stage 5 also auto-passes |
| **borderline-express** | qualifies, but ≥1 criterion needed a judgment call | present the brief, ask `express` / `full` / `abort` |
| **full** | any disqualifier | say which one, proceed to stage 2 |

Borderline is where the prompt earns its keep: a frontend edit that's mostly styling but also
touches one prop or one effect dependency; a lone constant you can't fully exclude from a
payments-adjacent path; a diff only partly designed in this session.

**Complete when** each of the six criteria has an explicit pass / fail / judgment-call verdict
against the actual file list, and the resulting class is stated.

---

## Express lane

Skip stages 2–4.5. One safety net stays on: if the diff touches any code or manifest file
(`pyproject.toml`, `tsconfig.json`, `package.json`), run the smallest `lint` from stage 3's table —
lint only, never tests. Pure prose skips even that.

Go to stage 5 with lane + reason, `git diff --stat`, commit list, and lint result (or
`verify: skipped (docs/config only)`).

Express has no `fix-first`: to change something, `abort`, edit, re-run.

---

## Full lane

### 2. Simplify (Codex)

Write-capable pass — Codex applies edits in place. (Distinct from the built-in `/code-review`,
which is review-only.)

Spawn `codex:codex-rescue`:

> Run a simplify pass on the ship surface (`git diff <baseline>`).
> Goals: drop duplication, improve naming, remove unused imports/branches, replace heavy patterns
> with simple ones, preserve behavior.
> Apply edits in place. Keep the public/behavioral surface unchanged.
> Report a one-line summary per file touched, and any item you deliberately left alone, with reason.

On a pre-committed surface these edits land as a new uncommitted layer; stage 6 folds them in.

**Complete when** Codex has returned and every file it touched is named in the summary.

### 3. Verify (behavior-preserving gate)

Detect the repo's gate from manifest presence, run the smallest relevant set, stop on first failure:

| Manifest | Gate |
|---|---|
| `uv.lock` | `uv run ruff check .` → `uv run pytest -x` (skip pytest with no `tests/` or `test_*.py`) |
| `pnpm-lock.yaml` / `package-lock.json` | defined `lint`, `typecheck`, `test` scripts |
| `Cargo.toml` | `cargo clippy -- -D warnings` → `cargo test` |
| `go.mod` | `go vet ./...` → `go test ./...` |
| none | log `verify: no gate detected` and continue |

On failure: spawn `codex:codex-rescue` with the failing command, last ~100 lines of stderr, and
"fix without changing public API surface or tests; preserve behavior." Re-run the failing command
**once**. Green → stage 4. Red → stop and hand the error plus Codex's diff back to the user.

**Complete when** the gate is green, was absent, or has failed twice and been handed back.

### 4. Review (Codex)

Spawn a second `codex:codex-rescue`:

> Independent code-quality review of the ship surface (`git diff <baseline>`).
> Read CLAUDE.md, ~/.claude/rules/*.md, and the nearest project AGENTS.md.
> Surface findings as Important / Nit with file:line; mark pre-existing issues as such.
> Comment-only — do not edit code. Cap Nits at 5; beyond that, say "plus N similar items".

**Complete when** the findings list is in hand, each carrying a file:line.

### 4.5. Verify-then-patch

Codex findings are **hypotheses**. It under-specifies real bugs (gesturing at "TZ correctness" when
the actual defect is a 5-line DST `Duration(days: N)` arithmetic error) and raises speculative ones
that don't survive a code read. For each Important and Nit:

1. **Read the flagged file:line yourself** and judge independently whether it is real.
2. Real findings default to **inline fix in this commit**. Defer only for a stated reason:

| Fix inline | Defer |
|---|---|
| Surgical: ≤ ~20 lines, no public-API change | Needs cross-repo investigation you can't finish now |
| Mechanical (rename, missing fixture, calendar-arithmetic swap) | Signature change with dependent callers |
| Test gap that's a few lines of fixture | Architecturally adjacent but outside the diff's intent |
| Latent bug in the same surface as the current change | Lower priority than queued work, user wants it bundled |

3. Apply the patches, then re-run the stage 3 gate. Green → the patch joins the commit. Red →
   revert the patch, reclassify as deferred, and say why.

Inline is the default because the originating change is the cheapest place to fix what the review
just surfaced, and follow-up tickets accumulate as debt.

**Complete when** every finding carries a verdict — `[patched inline]` with the fix, `[deferred]`
with the reason, or `[not real]` with what the code actually showed.

---

## Shared stages

### 5. Decision gate

**clean-express** (auto-routed at 1.5, lint green or skipped): print the one-screen summary and go
to stage 6. The user can interrupt before the push lands.

**borderline-express and full**: show the brief and wait for `ship` / `abort` / `fix-first`
(full only).

The brief carries: lane; final `git diff --stat`; simplify summary; verify result (clean / green
after Codex fix / green after inline patches); every finding with its 4.5 verdict.

- `fix-first` — loop back to stage 2 with the new diff.
- `abort` — exit with the working tree intact. In pre-committed state the commits also stay: abort
  means "don't push", not "undo".
- `ship` — stage 6.

Full and borderline runs wait for the explicit `ship` even when every Important finding was patched
and only deferred Nits remain.

**Complete when** the class-appropriate path resolved: summary printed for clean-express, or an
explicit user word received.

### 6. Commit & push

**Residue sweep first.** Cross-check every `git status --short` entry against the pre-flight ship
surface. Temp scripts, abandoned-approach leftovers, stray logs, one-off test files, and editor
droppings get deleted or `.gitignore`d before `git add -A`. Anything you can't classify, ask about.

- **Uncommitted**: draft a Conventional Commit — `feat|fix|chore|docs|refactor|test|perf`, colon,
  space, imperative subject under 70 chars, no period. Body optional and about *why*. Apply the
  `Co-Authored-By` trailer per CLAUDE.md Git Automation. Then
  `git add -A && git commit -m "<message>" && git push origin main`.
- **Pre-committed**: `git push origin main` (or `git push origin HEAD:main` from a worktree branch).
  When stage 2 or 4.5 added edits on top, agree with the user on amend vs. append first.

**Complete when** the push is confirmed and the new HEAD SHA is reported.

### 6.5. Observe

"Pushed" is not "done" — this is the deterministic form of CLAUDE.md's *done = observed*.

Repos with no downstream (docs-only, no push-to-main workflow in `.github/workflows/`) skip this
stage entirely; do not arm the gate.

Otherwise, immediately after the push:

```bash
uv run ~/.claude/hooks/verify_gate.py arm "<one-line task>" "CI/deploy run for <SHA> green" "changed surface observed (page renders / endpoint responds)"
```

Checks are phrased as observable end states. The Stop hook then blocks the turn from ending until
the gate clears.

Observe: `gh run list --commit <SHA>` → follow to green (`gh run watch <run-id>`). UI changes get
the affected page loaded, with a screenshot when the diff is visual; API changes get the endpoint
hit. Then `uv run ~/.claude/hooks/verify_gate.py clear` and put the evidence — run URL, observed
page or endpoint state — in the final report.

A red run is handled like a stage 3 failure: surface it with the failing job's output. Clearing the
gate is a claim that the end state was observed; after a deliberate abort, clear it and say so in
the same breath.

**Complete when** the gate is cleared with evidence in the report, or the stage was skipped for a
repo with no downstream.

### 7. Worktree cleanup

Stale worktrees under `.claude/worktrees/` break tooling that walks the repo — `shopify app dev`
aborts on a duplicate `shopify.web.toml`, and the same shape hits any CLI scanning `**/package.json`
or `**/*.toml`.

Run `git worktree list`. A worktree is a removal candidate when `git log origin/main..<branch>` is
empty **and** `git -C <path> status --short` is clean. Dirty worktrees, unpushed commits, and
branches with commits not in `origin/main` are left alone without a prompt.

Surface candidates (path + branch + last SHA), including the current one if `/ship` ran from it, and
ask before removing. On confirm, from the main repo: `git worktree remove <path>` then
`git branch -d <branch>` — `-d` refuses unmerged branches, which is the safety property being
relied on here.

If the removed worktree was the one `/ship` ran from, `cd` to the main repo and `git pull --ff-only`
so local `main` matches what was just pushed.

**Complete when** every candidate is removed or explicitly skipped, and local `main` matches
`origin/main`.

---

## Out of scope

- **Code not finished** → `/mattpocock-skills:grill-me` → `to-spec` / `to-tickets` → `implement`.
  `/ship` starts once the code exists.
- **PR-based work** → feature branch plus the `/code-review` plugin after pushing.
- **A worktree carrying unrelated uncommitted work from another task** → split it first.

Codex errors in stage 2 or 4 stop the pipeline and go back to the user; there is no auto-retry.
A rejected push (race) stops and asks whether to `git pull --rebase` and retry.
