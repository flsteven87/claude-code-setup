---
description: PR-completion auto-pilot for NexRex repos — review + auto-fix findings + merge open GitHub PR to main. Use when the user wants to take an existing open PR through to merged-on-main, including phrases like '/merge-pr', 'merge PR #X', '把 PR X 收掉', '把 PR 跑完', 'review then merge', '把 #N 推完'. Different from /ship which is solo main-branch push with no PR; this one is PR-based and uses `gh pr merge`. The pipeline auto-fixes small findings (inline patch + extra commit + continue) and only stops on 8 named blockers — your `/merge-pr <N>` invocation IS the approval. QA Agent runs downstream smoke tests, so review prioritizes contract / design / story correctness over exhaustive bug-hunting.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm:*), Bash(cargo:*), Bash(go:*), Bash(test -f:*), Bash(ls:*), Bash(grep:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Task, TaskOutput, SendMessage, TaskStop
disable-model-invocation: false
---

# /merge-pr — PR-completion auto-pilot

Drive an open GitHub PR through review → merge → post-merge cleanup. Default flow is **auto-pilot**: the user's `/merge-pr <N>` invocation is the approval, and Claude orchestrates Codex review, auto-fixes findings under a budget, runs the merge, and updates Linear / memory. The pipeline only stops for 8 named blockers (§ Blocker contract).

## Why auto-pilot

The previous merge gate paused on every finding for a `ship / abort / fix-first` decision. In practice, most findings are mechanical (helper rename, missing fixture, idiom drift) and the user-facing question was always "yes, just fix it." That's not gate-keeping, that's an approval ping that wastes minutes per PR.

This skill flips the default: **fix it and move on**, escalate only when the fix touches contract / design / story. QA Agent runs smoke tests downstream — so review's job here is to catch design / contract / scope issues, not 100% bug coverage.

---

## Pipeline stages

```
1. Pre-flight        — auth + PR fetch + repo / ticket / sibling-PR detection
2. Scope frame       — git diff main...PR-HEAD --name-only, AST-guard cross-check
3. Verify (NEX-733)  — lint/test, in-scope failures only
4. Codex review      — adversarial slice + PR-body-vs-diff + attack-surface picks
   ↳ Liveness watcher runs in parallel
5. Auto-patch loop   — Codex findings → inline patch + commit, bounded by budget
6. CHANGELOG check   — Unreleased entry present + roughly matches diff
7. Merge             — gh pr merge --auto --squash --delete-branch
8. Post-merge        — Linear Done + memory write-back + worktree cleanup
```

All stages have hard inputs/outputs — if a stage's preconditions miss, escalate to the matching blocker rather than improvising.

---

## Blocker contract (the 8 things that pause the pipeline)

These are the only reasons to ask the user. Surface as a tight one-screen brief, then wait for input.

| # | Blocker | Detect | Why pause |
|---|---|---|---|
| 1 | Auto-fix would change public API / behavior / cross-file signature | Codex finding tag includes `[behavior]`, `[api]`, or diff lines touch exported symbol declarations | This is redesign, not review |
| 2 | Auto-fix attempted, verify still red | Stage 3 re-run fails after Codex rescue pass | Root cause not on surface |
| 3 | Auto-fix budget exhausted | ≥ 100 net auto-patched LOC OR ≥ 5 auto-patches | Scope creep — Codex may be drifting from PR intent |
| 4 | CHANGELOG / Linear info un-inferrable | No `NEX-XXX` in PR title / branch / body AND Linear search by PR URL empty | Need user to identify ticket |
| 5 | PR body materially mismatches diff | Codex slice "PR-body-vs-diff" flags ≥1 claim with no backing code or contradicting code (NEX-855 pattern) | Three choices: rewrite body / change code / ship anyway — user calls |
| 6 | Diff-scope test red | Failing test imports cross diff fileset (see § In-scope test definition) | NEX-733 baseline only excuses out-of-scope red |
| 7 | `mergeable: CONFLICTING` or behind base by ≥10 commits | `gh pr view --json mergeable,mergeStateStatus` | Rebase strategy is a user call |
| 8 | Codex review liveness check failed | See § Liveness watcher | Review process appears stuck |

Linear ticket state ∈ {Cancelled, Done} folds into blocker #4 ("wrong ticket cited"). CI failures fold into blocker #2 once `gh pr merge --auto` rejects them. Sibling-repo PR missing folds into blocker #5 ("PR body implies the change is complete, but companion PR isn't ready").

---

## Stage 1 — Pre-flight

```bash
gh auth switch --user steven-wu-nexrex && gh pr view <N> -R NexRex-Dev/<repo> \
  --json number,title,body,headRefName,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,author,labels,url
```

Chain the auth switch with the actual op (single bash invocation) — session-level `gh auth` revert is real (per memory ops notes).

Extract:
- **Ticket ID**: regex `NEX-\d+` against PR title → branch name → body. First hit wins.
- **Linear state**: `mcp__linear__get_issue` on the ticket ID. Reject if state ∈ {Cancelled, Done} (blocker #4).
- **Sibling PRs**: list Linear ticket `attachments[]` for additional GitHub PR URLs. If found in a different repo and that PR is still open, flag for blocker #5 — **unless** the current PR body explicitly names the companion (`companion PR in repo-Y is #M`) OR contains backward-compat language (`legacy.*remain|backward.compat|preserv.*legacy|deprecated.*available`). In either case, soft-flag and continue.
- **Repo detection**: from `git remote -v` or explicit `--repo` arg. If user invoked from `nr-platform` working dir but PR is in `nr-app`, that's fine — just pin `-R NexRex-Dev/nr-app` on every `gh` call.

Don't checkout the PR locally — all read operations go through `gh pr diff` and `gh pr view`. Only checkout if a later stage needs to push commits (Stage 5 auto-patches).

If Stage 1 fails any check, surface the blocker and stop.

---

## Stage 2 — Scope frame + AST-guard cross-check

Compute the diff fileset:

```bash
gh pr diff <N> -R NexRex-Dev/<repo> --name-only
```

Cross-reference against the AST-guard table in MEMORY.md (line ~184-204 — "AST-pinned invariants"). If any diff path matches a guarded surface, log:

> ⚠️  PR touches `<file>`, guarded by `<test_path>`. Verify the guard still encodes the intended invariant. (This is a flag, not a blocker — the guard may legitimately need updating.)

The flag goes into the Stage 4 Codex brief so review focuses there. Don't pause.

Also compute imports graph for in-scope test definition (used in Stage 3 / blocker #6):
- For Python: `grep -r "from <changed-module-path>" tests/` finds dependent tests.
- For TS: lean on package-relative imports.
- Heuristic only — Codex review picks up anything this misses.

---

## Stage 3 — Verify (NEX-733-aware)

Run the smallest gate that matches the repo manifest. Same table as `/ship` Stage 3 — Python `uv run ruff` + `uv run pytest -x`, pnpm/npm scripts if defined, etc. **Flutter (`pubspec.yaml`)**: `flutter analyze` + `flutter test` scoped to diff fileset; if `flutter` not on PATH try `~/fvm/versions/*/bin/flutter`.

**Classification rule (NEX-733):**
- Failing test's source file IS in diff fileset → in-scope → blocker #6 candidate
- Failing test's source file imports a module in diff fileset → in-scope → blocker #6 candidate
- Neither → pre-existing red → log and continue

If anything is in-scope red, run ONE Codex rescue pass on the failure (single attempt, brief = stderr tail + "fix without changing public API"). If it stays red after rescue → blocker #2.

**Red sub-classification:** assertion / logic failure = treat as above. Collection error / `Connection refused` / import error = infra issue (e.g. Postgres not running locally); log it, skip-verify for this PR, do not revert patches. CI will catch real regressions.

Out-of-scope reds get one line in the final report: `Pre-existing red (cite NEX-734~739 cluster if applicable): N tests`.

---

## Stage 4 — Codex review

Spawn `codex:codex-rescue` as a **background subagent** with this brief:

> Independent adversarial review of PR #N (`gh pr diff <N> -R NexRex-Dev/<repo>`). Read CLAUDE.md, ~/.claude/rules/*.md, and any nearest project AGENTS.md.
>
> **Required slices (do all three):**
> 1. **PR-body-vs-diff consistency** — read PR body claim-by-claim. For each claim, locate backing code. Flag claims with no backing code or with backing code that does materially different work. (NEX-855 pattern.)
> 2. **Attack surface picks** — based on what the diff touches, pick 2-3 of: auth bypass / data loss / rollback safety / race conditions / degraded dependencies / version skew / observability gaps. State which ones and why.
> 3. **Tagged findings** — output Important / Nit / Pre-existing with file:line. Tag each Important with one of: `[mechanical]`, `[behavior]`, `[api]`, `[contract]`, `[story]`. (Tags drive Stage 5 routing.)
>
> Comment-only — do NOT edit code. Cap Nits at 5; for more, say "plus N similar items".
>
> If you (Codex) realize partway through that a finding requires architectural discussion, label it `[behavior]` or `[api]` so the orchestrator escalates correctly. Do not silently fix or skip.

While Codex runs, the orchestrator runs the **liveness watcher** (next section) — don't sleep-poll, use TaskOutput growth and SendMessage as the heartbeat.

---

## Liveness watcher

Codex review may take as long as it takes — **no hard time cap**. The user has explicitly approved unbounded review duration. What the orchestrator owes the user is **visible progress**, not a deadline.

### User-facing heartbeat (REQUIRED, 3-min cadence)

The user MUST see a one-line status update **every 3 minutes** while Codex is running. This is not optional; without it the user has no signal that the pipeline is alive vs. silently hung.

Implement with the **`Monitor` tool** (not `Bash run_in_background`). Each stdout line emitted by the Monitor command becomes its own notification delivered to the chat — that is the one-line heartbeat the user sees. `Bash run_in_background` only notifies on process completion, so it cannot deliver streaming progress.

Template — pass this as the Monitor `command`, adapting `CODEX_OUT` to the actual Codex task output path:

```bash
CODEX_OUT="<path-to-codex-task-output>"
start=$(date +%s)
last_size=$(wc -c < "$CODEX_OUT" 2>/dev/null || echo 0)
last_growth_ts=$start
while true; do
  sleep 180
  now=$(date +%s)
  elapsed=$(( (now - start) / 60 ))
  size=$(wc -c < "$CODEX_OUT" 2>/dev/null || echo 0)
  if [ "$size" -gt "$last_size" ]; then
    last_growth_ts=$now
    last_size=$size
  fi
  idle=$(( (now - last_growth_ts) / 60 ))
  printf "Codex review @ %dmin | %dB output | idle %dmin\n" "$elapsed" "$size" "$idle"
  # Terminal marker — Codex CLI prints "tokens used" at the end of every run.
  if grep -q "tokens used" "$CODEX_OUT" 2>/dev/null; then
    printf "Codex review: terminal marker reached, exiting watcher\n"
    exit 0
  fi
done
```

Monitor call shape: `description: "Codex review #<N> heartbeat (3-min cadence)"`, `timeout_ms: 3600000`, `persistent: false`. The orchestrator should NOT poll or check progress itself — each `printf` line arrives as its own notification (`Codex review @ 3min | 8KB output | idle 0min`), and the watcher exits when the terminal marker `tokens used` shows up in the Codex output file.

### Stuck detection

Stuck is defined by **idle time** (no output growth), not elapsed time. Thresholds:

| Idle delta | Action |
|---|---|
| `< 5 min` | Normal — Codex is reasoning or running a long tool call |
| `5–10 min` | One-shot nudge: `SendMessage(codex_id, "Liveness check — one-line status of current activity, then continue.")` |
| `> 10 min` after nudge with no growth | `TaskStop(codex_id)` → blocker #8 with partial output |

There is **no elapsed-time ceiling**. Reviews can run for 30, 60, 90+ minutes if Codex is genuinely working (output growing). The user's "review can take as long as needed" guarantee is what removes the ceiling — the cost of patience is just heartbeat noise, which is bounded at ~one line per 3 min.

### Why 3 min, not 1 min

1-min cadence creates 30+ heartbeat lines on a 45-min review — pure noise. 3-min cadence yields ~15 lines max on a long review, which is readable as a column in the transcript. It's also long enough that successive lines actually show movement (KB growth, tool calls advancing), so each heartbeat carries information instead of repeating the same numbers.

---

## Stage 5 — Auto-patch loop

For each Codex Important / Nit finding, in order:

1. **Read the flagged file:line yourself.** Codex findings are hypotheses, not conclusions. If grep + Read confirms the finding is wrong, mark `[rejected]` with reason and skip. Codex tags describe the finding domain, not the fix shape — if the underlying fix is small / test-only / comment-only and stays inside this PR's scope, treat it as `[mechanical]` even when Codex tagged it `[contract]` / `[api]`.
2. **Route by tag:**
   - `[mechanical]` / `[nit]` → auto-patch
   - `[behavior]` / `[api]` / `[contract]` → blocker #1
   - `[story]` → blocker #5
3. **Apply the patch.** Use idiomatic best-practice for the language. Don't over-engineer.
4. **Commit immediately** with subject `<type>(review): <one-line fix> [auto-patched from Codex review]`. One commit per finding — keeps the audit trail clean and easy to revert individually.
5. **Re-run Stage 3 verify** after each patch. Green → continue to next finding. Red → revert this patch (`git reset --hard HEAD~1`), tag finding `[deferred: caused verify regression]`, continue.
6. **Track budget:** cumulative net LOC (use `git diff <pre-patch-SHA>..HEAD --shortstat`) and patch count. Hit 100 LOC OR 5 patches → blocker #3.

After the loop, push the new commits to the PR branch: `git push origin <head-ref>`. This triggers CI on the PR with the patches included — `gh pr merge --auto` in Stage 7 will wait for that CI before merging.

If zero findings or all rejected → skip straight to Stage 6, no push needed.

---

## Stage 6 — CHANGELOG check

```bash
head -50 CHANGELOG.md
```

Look for the ticket ID under `## [Unreleased]`. If absent:
- Inferrable from PR title + body → write a one-line entry under the most appropriate `### Added` / `### Fixed` / `### Changed` and commit `docs(changelog): add NEX-XXX entry [auto]`. Push.
- Not inferrable (no clear category, no clear summary) → blocker #4.

If present but the entry text reads materially different from PR title/body — log a warning but **don't block**. The QA pipeline cares about behavior, not prose accuracy; users can polish CHANGELOG in a follow-up if needed.

---

## Stage 7 — Merge

```bash
gh pr merge <N> -R NexRex-Dev/<repo> --auto --squash --delete-branch \
  --subject "<conventional-commit subject> (#<N>)"
```

Subject convention (from memory ops): `<type>(<scope>): <imperative phrase> (#<N>)`. Examples: `fix(api): align Garmin onboarding backfill contract (#241)`, `chore(chat): remove orphaned AI Coach Socket.IO path (#225)`. Lift the type/scope from the PR title if it already follows conventional-commit shape; otherwise infer.

The `--auto` flag tells GitHub to merge when all required checks pass. If checks are already green, merge is immediate. If a check flips red after submit, GitHub holds and notifies — that becomes blocker #2 retroactively (orchestrator detects via `gh pr view --json mergeStateStatus` showing `BLOCKED`).

*Note for NexRex repos:* per NEX-831 cost cuts, PR-side checks are cheap-only (schema-validation, i18n parity, CodeRabbit) — `--auto` typically merges within seconds of submit. The race window is theoretical here, not practical.

Capture the squash SHA: `gh pr view <N> --json mergeCommit -q .mergeCommit.oid`. Will be used in Stage 8.

---

## Stage 8 — Post-merge

Three independent finalize actions — run in parallel where possible:

1. **Linear ticket → Done.** Use `mcp__linear__save_issue` with `state: "Done"`. Add a comment with: `Merged via #<N> as <squash-SHA>`.
2. **Memory write-back.** Append a one-liner to MEMORY.md "Current Phase" section's ship inventory: `PR [#<N>](url) (NEX-XXX <one-line>, merged <date> as <squash-SHA>)`. Don't restructure — just add the bullet.
3. **Local worktree cleanup.** `git fetch --prune origin` to drop the deleted remote branch. If the user is currently in a worktree for this branch, `cd` to main repo + `git pull --ff-only` + `git worktree remove` as in /ship Stage 7. If on main already, just pull.

Output a 4-line final report:
```
✅ Merged #<N> → <squash-SHA>
✅ Linear NEX-XXX → Done
✅ Memory updated
Patches applied during review: N (M net LOC) | Codex review: Tmin
```

---

## In-scope test definition (precise)

A failing test is **in-scope** for blocker #6 if either:
- The test's source file path appears in `gh pr diff --name-only`, OR
- The test's source file imports a module whose path appears in the diff fileset

Heuristic, not exact — but covers the realistic cases without needing a full dependency graph. If you're uncertain, treat as in-scope (false positive is "ran one Codex rescue," false negative is "shipped a regression").

---

## When NOT to use this command

- **Solo main-branch push (no PR)** — use `/ship`. This skill assumes a remote PR exists.
- **Draft PR / WIP review only** — this skill merges. For review-only on a draft, spawn Codex review manually.
- **Cross-repo coordinated release** — when two PRs must merge atomically, the auto-merge race window matters. Coordinate manually.
- **Hotfix bypassing CI** — explicitly out of scope. If you need to bypass checks, do it manually with full awareness.

## Failure recovery

- **Stage 4 Codex stuck (blocker #8)** — TaskStop happens automatically. Surface the partial output, ask the user "review partially complete, ship anyway / abort / restart Codex?"
- **Stage 5 auto-patch caused verify regression** — patch is auto-reverted, finding tagged `[deferred]`, loop continues. No user prompt.
- **Stage 7 merge rejected by `--auto`** — `gh pr view --json mergeStateStatus` will say `BLOCKED`. Surface which check failed; treat as blocker #2 (CI red after our changes).
- **Stage 8 Linear save fails** — log the error, leave the ticket alone (user can flip manually), continue. Memory write-back is independent and should still happen.

## Express path (when allowed)

If pre-flight detects all of:
- Diff ≤ 200 net lines AND ≤ 10 files
- Zero AST-guard hits
- No security-sensitive paths (auth/, payment/, webhooks/, RLS, migrations/)
- Single coherent commit subject
- Author is the current user (Steven)

Then skip Stage 4 (Codex review) entirely. Run Stages 1, 2, 3, 6, 7, 8 only. The auto-fix budget in Stage 5 becomes N/A (no findings to act on).

This is the equivalent of `/ship` Express lane, adapted for PR shape. Default is **full** — express only triggers when ALL conditions hold. No prompt; the conditions are deterministic.

## Invocation

```
/merge-pr <PR-number>
/merge-pr <PR-number> --repo nr-app          # explicit repo if not in current cwd
/merge-pr <PR-number> --full                 # force full lane even if express qualifies
/merge-pr <PR-number> --no-codex             # emergency: skip Codex review (still does verify + merge)
```

No interactive confirmation. The user's invocation is the approval.
