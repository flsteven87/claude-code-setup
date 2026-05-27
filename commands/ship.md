---
description: Solo / main-based ship pipeline — simplify (Codex) → review (Codex) → commit & push to origin/main. Express lane for small + clear diffs.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git stash:*), Bash(git worktree:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git rev-list:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm run:*), Bash(npm test:*), Bash(cargo:*), Bash(go vet:*), Bash(go test:*), Bash(test -f:*), Bash(ls:*), Task
disable-model-invocation: false
---

# /ship — End-to-end ship pipeline (main branch, no PR)

Drive a finalized change from working tree → committed → pushed to `origin/main`. Implementation review work is delegated to Codex per CLAUDE.md "Delegation to Codex" policy. This command is a thin orchestrator — each stage uses an existing skill or subagent.

Two lanes exist; the lane is chosen during pre-flight based on what the diff looks like.

| Lane | Stages | When |
|---|---|---|
| **Express** | 1 → 5 (light) → 6 → 7 | Small, clear diff with no load-bearing code semantics. Skips simplify + Codex review. |
| **Full** | 1 → 2 → 3 → 4 → 4.5 → 5 → 6 → 7 | Default. Any non-trivial code change, or anything the user wants gated through Codex. |

Lane selection is **auto-routed when every express criterion passes cleanly, surfaced for confirmation only when any criterion is borderline**. Pure docs / config / `.gitignore` / styling-token swaps auto-route to express without a prompt; cases where one criterion needs a judgment call get a prompt; everything else goes through full lane. The goal is to spend Codex tokens where they actually catch bugs and spend the user's time only on decisions that aren't obvious.

---

## Stages

### 1. Pre-flight

Detect what's actually being shipped. Don't assume a dirty working tree — multi-batch `/implement` runs and previously-confirmed commits both leave the repo in **pre-committed state** (clean tree, N commits ahead of `origin/main`).

```bash
git status --short
git rev-list --left-right --count origin/main...HEAD
```

Compute the **ship surface** = the aggregate change going to `origin/main`:

- If `git status --short` has entries → uncommitted changes are part of the ship surface; baseline is `HEAD`, diff is `git diff HEAD`.
- If working tree is clean AND `origin/main..HEAD` has commits → pre-committed state; baseline is `origin/main`, diff is `git diff origin/main..HEAD`.
- If both are empty → abort with `Nothing to ship.`

Run `git diff --stat <baseline>` to summarize. Show the user a one-screen summary including:
- Branch + ahead/behind state
- Files changed, lines +/-
- Commit list (if pre-committed) with one-line subjects

If unrelated staged changes appear mixed in, stop and ask whether to ship together or split.

### 1.5. Lane decision

Inspect the ship surface and **propose** a lane. Express qualifies when **all** of the following hold:

- **No load-bearing code**. Diff touches only files whose impact is local/textual: `.md`, `.txt`, `.rst`, `.gitignore`, `.editorconfig`, comments inside code files, `.env.example` (not real `.env`), top-level config docs. Anything under `src/`, `backend/`, `frontend/src/`, `migrations/`, `tests/` that contains real code logic disqualifies — **unless the change is purely textual / visual with the function-level contract unchanged**: pure renames, comments, docstrings, or styling-layer swaps (Tailwind class strings, design-token values like `oklch(...)`, colour / spacing constants in a `_helpers` / `tokens` file) where a code reader would treat the diff as a runtime no-op except for appearance.
- **No security-sensitive surface**. Authentication, authorization, RLS policies, payment flows, webhook receivers, secrets handling, CORS / CSP — even small changes here go through full lane. The blast radius of a wrong call is too high.
- **No schema or migration changes**. Any `migrations/*.sql`, Pydantic model field changes, GraphQL schema, OpenAPI spec → full lane.
- **Small in absolute terms**. ≤ ~200 net lines of meaningful change (auto-generated mass deletions like untracking a directory don't count; a 600k-line `git rm --cached` for a gitignore policy fix is still express-eligible). ≤ ~10 files of meaningful change.
- **Single coherent concept**. One commit (or N commits already explicitly discussed and chained). Not a grab-bag of unrelated fixes.
- **Already understood in this session**. The change was designed or reviewed in the current conversation, so the user has full context. If the user just opened a stale worktree from a week ago, default to full lane.

Classify the run:

- **clean-express** — every express criterion passes with a clear ✅, including the load-bearing-code exemption (pure docs / config / styling / token swaps). Announce the lane + per-diff reasoning in one screen and **proceed immediately** — no prompt at 1.5, and stage 5 will also auto-pass for this classification (see stage 5). User can Ctrl-C any time before the push lands.
- **borderline-express** — express qualifies but at least one criterion needed a judgment call (e.g., touches code under `frontend/src/` and you're not 100% sure it's a pure styling / no-op swap; or one constant in a payments-adjacent path you can't fully exclude). Present the brief and ask for `express` / `full` / `abort`.
- **full** — at least one disqualifier hit (security, schema, real code-logic change, multi-concept diff, stale-context, oversized). Say so in one line and proceed to stage 2 — no decision prompt.

Rationale: the user can interrupt before commit. A clean-express diff doesn't earn its prompt — typing `express` adds friction without changing the outcome. Borderline cases are exactly where the prompt earns its keep; that's when we ask. The previous default of "always ask when express qualifies" optimized for the high-stakes minority (auth / payment 5-line tweaks) at the cost of the low-stakes majority (docs, gitignore, styling). Those high-stakes cases are already caught by stricter criteria (security / schema / real-logic disqualifiers), not by gating every express run.

---

## Express lane (stages 5 → 6 → 7)

Skip stages 2 (simplify), 3 (verify), 4 (Codex review), 4.5 (verify-then-patch). The diff has been judged too small or too low-blast-radius for them to earn their keep.

One safety net stays on: if the diff contains **any** code file (even a config like `pyproject.toml`, `tsconfig.json`, `package.json`), run the smallest detectable lint check from stage 3's manifest table — but only `lint`, never tests. Skip even that if the diff is pure prose/markdown.

Then go to **stage 5 (decision gate)** with a one-screen express summary:
- Lane chosen and why (one line)
- `git diff --stat`
- Commit list (if pre-committed)
- Lint result if applicable, else `verify: skipped (docs/config only)`

Wait for `ship` / `abort`. No `fix-first` option in express lane — if the user wants changes, they say `abort` and edit, then re-run /ship.

Then proceed to stage 6 (push) and stage 7 (worktree cleanup).

---

## Full lane (stages 2 → 3 → 4 → 4.5 → 5 → 6 → 7)

### 2. Simplify (Codex)

> ⚠️ Distinct from Claude Code's built-in `/code-review` (formerly `/simplify`, made review-only in 2.1.147). This stage is **write-capable** — codex-rescue applies edits in place. Naming kept because the goal (drop duplication, improve naming, preserve behavior) is the original `/simplify` shape, not the new `/code-review` shape.

Spawn `codex:codex-rescue` subagent with this brief:

> Run a simplify pass on the ship surface (the diff identified in pre-flight; use `git diff <baseline>..HEAD` if pre-committed, else `git diff HEAD`).
> Goals: drop duplication, improve naming, remove unused imports/branches, replace heavy patterns with simple ones, preserve behavior.
> Apply edits in place. Keep the public/behavioral surface unchanged.
> Report a one-line summary per file touched and any items where you intentionally did NOT simplify (with reason).

Wait for completion. If the original ship surface was pre-committed, Codex's edits will land in a new uncommitted layer — that's fine, they'll be folded in at stage 6 either by amending or with a follow-up commit (Claude's call based on whether the user wants a clean single commit or a "+ simplify pass" trailer).

### 3. Verify (auto, behavior-preserving gate)

Detect the repo's gate scripts from manifest presence and run the smallest relevant set. Stop on first failure.

- **Python (`uv.lock`)**: `uv run ruff check .` → `uv run pytest -x` (skip pytest if no `tests/` or `test_*.py`)
- **pnpm (`pnpm-lock.yaml`)**: existing `lint`, `typecheck`, `test` scripts (skip ones not defined)
- **npm (`package-lock.json`)**: existing `lint`, `typecheck`, `test` scripts
- **Cargo (`Cargo.toml`)**: `cargo clippy -- -D warnings` → `cargo test`
- **Go (`go.mod`)**: `go vet ./...` → `go test ./...`
- **No manifest match**: log `verify: no gate detected, skipping` and continue.

**On failure:**
- Spawn `codex:codex-rescue` with brief: failing command + last ~100 lines of stderr + "fix without changing public API surface or tests; preserve behavior."
- After Codex finishes, re-run the failing command **once**.
- Pass on retry → continue to stage 4.
- Fail on retry → STOP. Surface error + Codex diff to user. Do NOT auto-retry further.

### 4. Review (Codex)

Spawn a second `codex:codex-rescue` subagent with this brief:

> Independent code-quality review of the ship surface (`git diff <baseline>..HEAD` if pre-committed, else `git diff HEAD`).
> Read CLAUDE.md, ~/.claude/rules/*.md, and any nearest project AGENTS.md.
> Surface findings as Important / Nit / Pre-existing with file:line.
> Comment-only — do NOT edit code. Cap Nits at 5; for more, say "plus N similar items" in summary.

### 4.5. Verify-then-patch findings (inline by default)

Codex findings are **hypotheses**, not conclusions. Codex sometimes under-specifies a real issue (gesturing at "TZ correctness" when the actual bug is a 5-line DST `Duration(days: N)` arithmetic problem) or flags speculative concerns that don't survive a code read. So for each Important / Nit:

1. **Read the flagged file:line yourself.** Decide independently whether the finding is real.
2. **If real, decide inline-fix vs defer using these criteria:**

| Inline-fix in this commit | Defer to follow-up ticket |
|---|---|
| Surgical: ≤ ~20 lines, no public-API change | Needs cross-repo investigation you can't complete now |
| Mechanical (helper rename, missing test fixture, calendar arithmetic swap) | Non-trivial blast radius (signature change, dependent caller updates) |
| Test gap that's a few lines of fixture | Real but lower priority than other queued work, user wants to bundle later |
| Latent bug in the same surface area as the current change | Architecturally adjacent but outside the diff's intent |

3. **Apply the inline patches yourself.** Re-run the stage 3 verify gate after patching — if it stays green, the patch joins the same commit. If it goes red, revert the patch, treat it as defer, and tell the user why.

The default is **inline**. Deferring should be a deliberate call with a stated reason, not a reflex. The previous "merge with caveats + follow-up ticket" pattern accumulated debt — follow-up tickets often never get prioritized. The original change is the cheapest place to fix something the review just surfaced, and the user already has context for that surface area.

---

## Stages shared by both lanes

### 5. Decision gate (user)

**Clean-express runs** (auto-routed at stage 1.5 with no borderline criteria, lint passed cleanly or skipped): print a one-screen summary — lane + per-diff reasoning + `git diff --stat` + lint result (or "skipped") — and **proceed straight to stage 6**. No prompt. User can Ctrl-C any time before the push.

**Borderline-express and full runs**: show the brief and wait.

Show:
- Lane (express / full)
- Final `git diff --stat` (reflects original + simplify + inline patches, whichever applied)
- Simplify summary (full lane only)
- Verify result (full lane only) — passed cleanly / passed after Codex fix / re-passed after inline patches
- Review findings (full lane only), each tagged **[patched inline]** with one-line fix description OR **[deferred]** with the reason (criteria from 4.5)

Wait for user reply: `ship` / `abort` / `fix-first` (full lane only).
- `fix-first` — user wants more changes before merging; loop back to stage 2 with the new diff. Express lane has no `fix-first` — the user aborts, edits, re-runs.
- `abort` — exit, working tree intact (in pre-committed state, the existing commits also remain — abort means "don't push", not "undo commits").
- `ship` — continue to stage 6.

If every Important finding was patched inline and the user only sees deferred Nits with reasons, you should still pause for the explicit `ship` — never auto-proceed.

### 6. Commit & push

Branch on the ship-surface shape:

- **Uncommitted state**: draft a **Conventional Commit** message (prefix one of `feat|fix|chore|docs|refactor|test|perf`, colon, space, imperative subject under 70 chars, no period; body optional, focus on *why* not *what*; no `Co-Authored-By` unless project CLAUDE.md specifies). `git add -A && git commit -m "<message>" && git push origin main`.
- **Pre-committed state**: commits already exist. Just `git push origin main` (or `git push origin HEAD:main` if shipping from a non-main branch like a worktree). If stage 2 / 4.5 added uncommitted edits on top, decide with the user whether to amend the last commit or append a new one before pushing.

Confirm push succeeded and report the new HEAD SHA.

### 7. Worktree cleanup (post-push)

Stale worktrees under `.claude/worktrees/` break tooling that walks the repo (e.g. `shopify app dev` aborts on duplicate `shopify.web.toml`; same shape for any CLI that scans `**/package.json`, `**/*.toml`, etc.). Clean them as part of ship so they don't accumulate.

- Run `git worktree list`. For each worktree under `.claude/worktrees/`, check whether its branch is fully merged into `origin/main`: `git log origin/main..<branch>` is empty AND `git -C <path> status --short` is clean.
- Surface candidates to the user (path + branch + last-commit SHA) and ask before removing. Include the **current** worktree if /ship ran from one and it now qualifies.
- On confirm, for each:
  - `git worktree remove <path>` (run from the main repo, not from inside the worktree being removed)
  - `git branch -d <branch>` — `-d` is safe; it refuses unmerged branches. Never use `-D`.
- Skip (do not prompt) any worktree that is dirty, has unpushed commits, or whose branch has commits not in `origin/main`.

If /ship ran from inside the current worktree and that worktree is now being removed, also `cd` to the main repo and `git pull --ff-only` so the local `main` matches what was just pushed.

---

## When NOT to use this command

- Implementation isn't done — use brainstorming → writing-plans → executing-plans first; `/ship` starts after code is written or after a deliberate commit.
- PR-based work — use a feature branch + the `/code-review` plugin after pushing.
- Mixed worktree with unrelated uncommitted changes from other tasks — split first.

## Failure modes

- Codex errors in stage 2/4 — stop, surface to user, do NOT auto-retry.
- Verify failure (stage 3) — one Codex rescue attempt; if retry still fails, stop and hand back to user.
- Push rejected (race) — stop, ask whether to `git pull --rebase` and retry.

## Express lane — examples vs counterexamples

To calibrate the lane decision, here are concrete cases that pattern-match each direction.

**Clean-express (auto-route, no prompt):**
- A `.gitignore` policy change + 4 docs files explaining the policy (this very skill's first user case).
- Fixing a typo in a `README.md` or a `CLAUDE.md` instruction.
- Adding a missing file to `.gitignore` after observing it accidentally tracked.
- Tightening a sentence in an existing `docs/architecture/<topic>.md`.
- Adding a new entry to a `references/` glossary.
- **Pure styling / design-token swap** — tightening a Tailwind class palette in a frontend `_helpers` / `tokens` file (e.g. swapping `text-success` / `text-warning` to `text-foreground` for type tags that shouldn't borrow alert tokens), changing `oklch(...)` values, dropping a hard-coded colour for a theme token. Contract unchanged, runtime behaviour identical, only visual output changes.

**Borderline-express (express qualifies, but ask before going):**
- A single-line constant change in a file you can't fully confirm is outside a payments / auth / RLS adjacency.
- A frontend code edit that's mostly styling but also touches one prop or one effect dependency — you're 90% sure it's no-op but not 100%.
- A diff that was *partially* designed in this session but partially predates it.

**Express lane does NOT fit (even if small):**
- A 3-line change to a webhook handler's signature validation.
- A 1-line change to a Supabase RLS policy.
- Adding a new `@field_validator` to a Pydantic model — touches schema semantics.
- A 5-line constant change in a payment / pricing path.
- A "just one line" diff in `auth.py` or anything under a `security/` directory.

When in doubt, ask the user. The cost of one extra Codex review pass is a few minutes and some tokens; the cost of shipping a broken auth path is much higher.
