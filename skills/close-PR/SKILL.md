---
name: close-PR
description: Use when the user says /close-PR or wants to take a PR all the way to merged with best-practice fixes applied along the way. Runs locate → review-change → simplify → codex-pushback → fix-in-place → verify → squash-merge → post-merge cleanup. The agent owns the merge: review findings + Codex push-back are remediated in-PR (not handed back to author) unless they hit an architectural / cross-stream stop trigger. Triggers on '/close-PR', 'close this PR', 'gate this PR', 'deep review this PR', '深度 review 這個 PR', '把這 PR 收掉', '收這個 PR', 'merge gatekeeper'.
---

# Close PR — Deep Review → Fix → Merged (Highly Automated)

```
locate → review-change → simplify → codex-pushback → fix-in-place → verify → squash-merge → post-merge-cleanup
```

**User-facing output: zh-tw** (per CLAUDE.md). SKILL structure stays English.

## What this skill is

End-to-end PR finisher. The agent OWNS the merge — invoking `/close-PR` is full delegation. Findings from review-change, simplify, and Codex are fix material, not handoff material. Default outcome: **merged + clean, with a 2-line confirmation back to the user**. Anything more verbose is wasted ink.

This is not for ad-hoc analysis or feature work. For author-side flow use `/ending` instead.

## Cardinal rule: ship it, don't narrate it

You are the merge owner. Don't pile blockers and lob them back — there often isn't another author. Every finding is YOUR todo, not a report.

Hard requirements (skipping any of these is skipping the phase):

- `Skill review-change` + `Skill simplify` MUST be real Skill tool calls. Manual diff reading is not a substitute.
- Codex push-back MUST be a real `Agent(subagent_type="codex:codex-rescue", ...)` dispatch. No self-simulation. Hand-rolling `codex exec` is forbidden (pipes swallow stream, HEREDOCs fragile, >500 char prompts blow up).
- Phase 4.5 fix-in-place: every Critical/High/Medium finding is fixed in-PR OR has a documented stop-trigger code. Default is fix.
- Verify gate runs real commands AFTER fixes. "Tests should pass" without running them is forbidden.
- Squash-merge is `gh pr merge <N> --squash --delete-branch` — no other path.
- Post-merge: Linear → Done + MEMORY.md edit + clean local main.

The first time you draft a "blocker — author needs to fix X" line, ask: is X covered by a stop trigger 1–8? If not, **fix X yourself**.

## Stop triggers (when fix-in-place is NOT the answer)

Fix-in-place is the default. The agent stops and asks the user ONLY when one of these objective triggers fires:

1. **🔴 Absolute Prohibition violation** — fix would require touching code listed in CLAUDE.md `Absolute Prohibitions` (e.g. removing schema validation, disabling RLS, adding `FORWARDED_ALLOW_IPS=*`). Surface verbatim.
2. **Scope blast** — fix touches files outside the PR diff scope by more than ~30% file growth, or pulls in a sibling service the PR didn't claim. Trigger an explicit user decision: "expand scope or split into follow-up?"
3. **Cross-stream ownership** — fix needs another team / agent / PR to land first (e.g. "this depends on NEX-XXX which is unmerged"). Surface the dependency.
4. **Genuine product / architecture decision** — finding implies "should we do X or Y?" with no defensible default in CLAUDE.md, MEMORY.md, or repo precedent. Examples: pricing model, API contract change, choice between two equally-valid auth strategies.
5. **Stacked PR detected in Phase 1** — open PRs target this branch's head. Merge order matters; surface to user.
6. **PR not authorized for ship** — wrong owner / cross-stream / no prior authorization signal. Don't merge silently.
7. **Mode-detection ambiguous** — PR has uncommitted local changes mixed in, branch diverged unexpectedly, mergeStateStatus undefined.
8. **Over-engineered capability surfaced by Phase 4.25** — fixing the findings would land a feature whose ongoing operational cost exceeds its value at current usage. Surface the cheaper alternative; let the user choose ship-as-is / drop-the-feature / replace-with-simpler.

Anything else — mechanical (lint, naming, dead code), bounded logic (≤2 files), missing test coverage for a fix you just applied, deploy-pattern alignment, runbook polish, schema mismatch with documented contract, alert-rule timing — **fix it in-PR**. Don't ask permission for things the project's own conventions already answer.

When a stop trigger fires, print: phase, specific trigger code (1–8 above), the minimal question needed to unblock, and the partial state already applied (so the user can decide based on what's already in the branch). No multi-option menus. Don't stop on 🟢 Low / non-trigger 🟡 Medium — surface in report and continue.

## Don't stop until done

Invoking `/close-PR` is full autonomous consent for the entire pipeline including squash-merge.

**The cardinal rule is: don't end the turn until the pipeline is done.** Brief progress text between phases is fine — actually preferred for transparency. What is NOT fine is ending the assistant turn before reaching the merge (or a real stop trigger). One short sentence per phase max; never let a sentence be the LAST thing emitted unless the pipeline is genuinely complete.

The failure mode this rule prevents (recurring in past close-PR runs):
- Sub-skill returns → caller writes a one-line recap → caller emits no follow-up tool call → turn ends → user has to ping "繼續" / "為什麼又停下來"

The fix is simple: **every text emit between Phase 1 and the final completion report must be followed by another tool call in the same response.** If you find yourself typing without queueing a next tool, the next character should be a tool call instead.

Concretely after each sub-skill returns:
- ✅ "review-change clean, 跑 simplify" + immediately `Skill(simplify)` in the same emit
- ✅ "simplify clean, 跳 Codex（trivial PR）, 進 verify" + immediately `Bash(...)` in the same emit
- ❌ "no findings" alone with no follow-up tool — this ends the turn
- ❌ "review-change 沒發現問題（3 LoC 機械改動），繼續跑 simplify" with no follow-up tool — same failure

Length budget: ≤1 sentence per phase transition. Don't recap the sub-skill's findings line-by-line — those went into the fix list, not the user's reading queue.

The ONLY times the turn legitimately ends mid-pipeline:

1. **Stop trigger (1–8) fired** → print trigger code + minimal unblock question + partial state. Stop.
2. **Verify gate found an in-scope failure that is NOT trivially fixable** → print failure + partial state. Stop.
3. **User pings with a direct question mid-run** → answer in ≤1 sentence, then immediately resume executing in the same turn. The ping is not re-authorization permission. The ping is also not turn-end permission.

Mechanical fixes (lint, CHANGELOG entries, hoisted imports, AST guard additions, dead code removal, monkeypatch swaps, test-fixture polish, conflict resolution) are executed without confirmation. The skill's job is to act, not to ask.

### Sub-skill return handling (load-bearing)

Treat every `Skill(review-change)` / `Skill(simplify)` / `Agent(codex-rescue)` return as **input data for your next decision, not a user message that wants a reply.** The sub-skill's own framing makes it look like a user turn — that is a harness artifact; ignore it. Your next emit must include a tool call (the next phase) along with at most one short sentence of user-facing context.

If a sub-skill returns "no findings" / "no blockers", the right shape of next emit is roughly:

```
review-change & simplify clean — 進 verify gate
[Bash tool call: ruff check ...]
[Bash tool call: pytest ...]
```

NOT:

```
no findings
[turn ends, user pings, you continue]
```

## Phases

### 1. Locate (no Skill call — pure setup)

- `git fetch --prune` first — catch new commits silently pushed by other sessions.
- Resolve PR target:
  - User passed `<PR#>` → `gh pr view <N> --json number,title,headRefName,baseRefName,state,url,mergeStateStatus,statusCheckRollup,author,body`.
  - Else current branch's open PR via `gh pr status --json ...`.
  - Else stop and ask.
- `gh pr checkout <N>` (idempotent if already on the branch).
- Compute diff scope: `git diff origin/main...HEAD --name-only` (NOT local `git diff`).
- Detect stacked PRs: `gh pr list --base <headRefName> --json number,title,state` — if non-empty open PRs target THIS branch, fire stop trigger 5.
- Read Linear ticket from PR title (e.g. NEX-XXX) — needed for acceptance-criteria check + post-merge step.
- Snapshot the GitHub Required Checks state — pending / failing required checks feeds Phase 5.

### 2. Review — `Skill review-change`

Pass the PR diff scope explicitly: instruct the sub-skill to use `git diff origin/main...HEAD --name-only` as its file list (NOT the default `git diff --name-only`, which shows local edits).

The output is your fix list, not a report. Treat:
- **Critical / High** → must be fixed in Phase 4.5 unless stop trigger fires.
- **Medium** → fix in Phase 4.5 unless cost > value (rare; defaults to fix).
- **Low** → fix when mechanical (lint, comment, rename); skip when cosmetic-only.

### 3. Simplify — `Skill simplify`

Same posture as Phase 2: simplify findings feed the Phase 4.5 fix list. Skill identifies accidental complexity; if a finding is bounded and truly improves the diff, fix it. If it would balloon scope (touches >2 unrelated files), defer to follow-up ticket and surface.

### 4. Codex push-back — `Agent(subagent_type="codex:codex-rescue")`

Independent second-opinion via Codex (gpt-5.5). Same model auditing its own diff misses systematic gaps — Codex routinely catches push-back items that single-model self-audit doesn't see (Pushgateway TTL, AC vs delivered scope drift, schema-vs-contract mismatch, etc.).

Dispatch the rescue subagent with a self-contained prompt. Required inputs in the prompt:

- **Repo + branch** — absolute path + `<headRefName>` so Codex can `git diff origin/main...HEAD` itself.
- **PR title + description** — copied from `gh pr view <N>`.
- **Linear ticket title + acceptance criteria** — pulled via `mcp__linear__get_issue`. Codex needs the AC verbatim to catch "shipped scope drifted from AC" gaps.
- **Phase 2 review-change findings** — verbatim, ordered by severity. Tell Codex NOT to restate them.
- **Phase 3 simplify findings** — verbatim. Same instruction.
- **Project 🔴 rules summary** — top 5–10 Absolute Prohibitions from `CLAUDE.md` (don't paste the full file).

Required ask in the prompt — frame it as adversarial review:

```
You are doing an independent merge-gate review. The first pass already ran and
will FIX (not block on) everything it found. Your job is NEW signal — what else
must be fixed before we can merge with confidence?

Look for:
- Silent behavior changes hidden in "refactor" hunks
- Regressions the existing tests don't cover
- Architecture / convention violations the first pass rationalized away
- Acceptance-criteria drift (delivered scope vs Linear AC)
- Stop conditions the first pass should have hit

If clean, say "no blockers" + 2 sentence why. Do NOT restate first-pass findings.
```

Treat Codex output:
- **Blocker items** → feed Phase 4.5 fix list. Don't bounce back to user; don't rationalize away. The point is to fix them.
- **Worth-a-follow-up items** → log as follow-up ticket candidates; fix in-PR ONLY if mechanical and bounded.
- **No blockers** → record as evidence in completion report, continue to Phase 4.5 (which then has nothing Codex-side to do).

For trivial PRs (≤30 LoC diff, docs-only, version-bump-only), this phase MAY no-op. The skill itself decides — set a token budget guard in the prompt.

### 4.25. Scope sanity / over-engineering check (NEW — runs once on aggregate findings)

Before applying any Phase 4.5 fix, look at the AGGREGATE of findings from Phases 2 + 3 + 4 and ask one meta-question:

> If we fix everything as listed, do we land a feature whose ongoing operational cost exceeds its value at current usage?

This is NOT a per-finding decision — it's a single check on the shape of the resulting deliverable. Most PRs sail through; the rare PR that fails is one where multiple findings cluster around the same component AND the fixes individually look reasonable AND together they reveal the component should be smaller (or absent).

**Cluster signals** (any one is enough to trigger the check):

- **Three or more findings** stem from one new feature/component AND each fix introduces a new dependency the codebase did not have (new credential, new manual ops step, new external service contract, new monitoring artifact).
- **Fix introduces a long-lived secret / JWT / auth flow** that does not already exist in repo and is not on the documented platform inventory.
- **Feature ships in a "disabled by default" state** because there is no safe way to enable it at deploy time — `suspend: true`, `feature_flag: false`, `if False:`, secret-keyref-required, etc.
- **Codex flagged AC-vs-delivered drift** AND the proposed fix to close the gap requires ops bandwidth the team does not currently have.
- **The capability's stated benefit overlaps ≥80% with something already present in the diff** — e.g. synthetic probe alerting overlaps with SLO burn-rate alerts on real traffic.
- **Activation cost of the capability is bigger than its benefit budget** — bringing it online needs more credentials/ops steps than the benefit warrants this quarter.

**If none of the above triggers:** continue straight to Phase 4.5; this phase is a no-op.

**If one or more triggers fire:** stop, surface to the user with this exact shape (zh-tw):

```
偵測到可能過度工程化：<one-line capability name>

訊號：
- <signal 1>
- <signal 2>
...

選項：
A. 照原計畫修（land 全部 fix；接受新增的 ops/credential cost）
B. 砍掉這個 capability（保留 PR 其他價值，從 diff 移除這部分）
C. 替換成更簡單版本（描述 80% 覆蓋率的替代方案；要動 N 行）

我傾向 <A/B/C>，理由：<one sentence>。
```

Then fire stop trigger 8. Wait for user choice. After the user chooses:
- A → drop into Phase 4.5 unchanged.
- B → replace the affected fix-list entries with a "remove the capability" fix; continue Phase 4.5.
- C → replace the affected entries with the simpler-version fix; continue Phase 4.5.

This check exists because some over-engineering is invisible at the per-finding level: each individual fix looks like sensible engineering, but the sum is a capability the team will never afford to operate. The clearest tell is `suspend: true` / `feature_flag: false` shipping in main — if we can't safely turn it on, we're carrying review cost for a capability we won't use.

NOTE: Don't use this phase to second-guess deliberate phased rollouts that the ticket / RFC explicitly calls for. The trigger is "the cluster of findings reveals we shouldn't have built this yet", not "I personally would have done it differently". When in doubt, lean toward A (ship as planned) — but voice the doubt so the user can override.

### 4.5. Fix-in-place loop (NEW — load-bearing phase)

Aggregate the fix list from Phases 2 + 3 + 4. Walk it. For each finding:

1. Decide: **fix-in-place** (default) or **stop trigger fires** (one of 1–7 above).
2. If fix-in-place:
   - Apply the change. Touch only files needed for that finding.
   - If the finding implies a test gap, add a test alongside the fix.
   - If the finding implies runbook / CHANGELOG drift, update those too.
3. If stop trigger fires: record the trigger code + the partial state, continue with the rest of the list.
4. After all in-place fixes are applied, re-confirm:
   - No file outside `git diff origin/main...HEAD --name-only` (pre-Phase-4.5) was newly added beyond the bounded growth budget.
   - No 🔴 Absolute Prohibition was crossed.

Common fix patterns this phase handles:
- **Schema / contract mismatch** (Codex caught wrong field name) — fix the call site.
- **Alert / monitoring timing drift from AC** — adjust `for:` durations and cron schedule.
- **Deploy registration gaps** (e.g. cronjob not in deploy-workers-prod.yml allowlist) — add the registration.
- **Defense-in-depth obvious gaps** (e.g. unauth `/metrics` endpoint with documented network-only mitigation) — add cheap auth gate using existing env-var pattern.
- **String-typed checks** → `isinstance` with proper import.
- **Missing test coverage on the fix path** — add the test.
- **CHANGELOG format drift** — fix in-place.
- **Inline imports, dead code, naming aliases** — clean up if bounded.

This phase is the difference between "merge-gate as report" and "merge-gate as ship". The first time you find yourself drafting a "blocker — author needs to fix X" line, ask: is X covered by a stop trigger? If not, **fix X**.

### 5. Verify — regression gate (the actual merge gate)

Load-bearing phase. Runs AFTER Phase 4.5 fixes are applied (and committed locally — do not push yet). Real commands; the output is its own proof.

Run, in order:

1. **Project CI commands** per `CLAUDE.md` for the changed paths:
   - Python changed → `uv run ruff check <changed .py paths>` + scoped `uv run pytest <test files for changed paths> -x --tb=short -q`.
   - Frontend changed → `npm run lint && npm run type-check && npm test` in the affected app dir.
   - Adapt to the actual repo layout (e.g. `api/`, `workers/`, `web/`).
   - **Scope rule — keep it tight.** Map each changed source file to its specific test file(s) (`api/core/X/foo.py` → `tests/unit/X/test_foo.py`); also include any new test files added in the diff. Do NOT broaden to the parent test directory "for safety" — that's slow + redundant. The full-sweep job is GitHub Actions' `CI - Test` (handled in step 4); local verify must be tight enough to finish in seconds, not minutes. If you can't enumerate the affected tests confidently, that's a signal to map them, not to widen.
2. **Pre-existing red filter** — for each failure, check whether the failing test/file is in the PR diff scope.
   - In scope (including any file Phase 4.5 modified) → blocks merge → go back and fix.
   - Not in scope → pre-existing main red, note in report, do NOT block (per NexRex MEMORY "CI Baseline" / "Session Role" rules).
3. **CHANGELOG check** — confirm an entry exists under `## [Unreleased]` (or matching release section), in the right `### Added/Fixed/Changed` group, ending with `(NEX-XXX)`. Phase 4.5 should have already fixed format drift.
4. **GitHub Required Checks** — push fixes to PR branch (`git push`). The remote `CI - Test` job runs the full broad-sweep suite, which on this repo carries a chronic layer of pre-existing main red (Jeffrey-owned canaries, in-flight invariants, integration tests against unprovisioned infra — see NexRex MEMORY "CI Baseline"). **Do NOT block on remote CI for failures that are out-of-PR-diff-scope, and do NOT poll CI just to re-confirm pre-existing red.** Specifically:
   - The local scoped pytest from step 1 + the AST-pinned invariant tests for any source file the PR touched are the authoritative gate for in-scope correctness. If those are green, in-scope behavior is verified.
   - For each `CI - Test` failure that surfaces, prove pre-existing in seconds: `git checkout main` → `uv run pytest <those exact test ids> -q` → if also red on main, it's pre-existing and merge is unblocked. Document the test path + the on-main-also-red proof in the report ("pre-existing main red, not regression").
   - Skip waiting on remote CI entirely when (a) you've already verified all currently-failing tests are pre-existing on main, AND (b) the diff doesn't touch code paths whose tests you can't map confidently. Polling 3+ minutes for CI to confirm the same OOS errors wastes turn budget.
   - WAIT for remote CI only when (a) the diff touches code paths whose tests you cannot map confidently to local files, OR (b) you have not yet verified main's baseline status for the failures you're seeing.
   - Required checks that ARE in scope (test files Phase 4.5 modified, lint on changed files, the diff's own new tests) MUST pass locally — if those are red, debug + fix and re-push.
5. **Ultrathink the diff post-fixes** — re-read each hunk and answer truthfully:
   - Did Phase 4.5 introduce silent behavior changes the tests don't cover?
   - Could the fixes break a currently-passing path?
   - Does each line follow project best practice (naming, layering, no `any`, no defensive boilerplate, no scope creep)?
   - Does the PR violate any 🔴 rule in project `CLAUDE.md`?

Any "not confident" → go back to Phase 4.5, do not merge to discover regressions in main.

### 6. Squash-merge

Only when Phase 5 is fully clear AND Phase 4.5 fixes are pushed AND CI is green (or the only red is documented pre-existing):

```bash
gh pr merge <N> --squash --delete-branch \
  --subject "<type>(<scope>): <summary> (#<N>)"
```

Subject pattern follows project's conventional-commit style. Type/scope inferred from PR title or the diff (api, workers, web, docs, deploy, etc.). Match existing repo precedent.

### 7. Post-merge cleanup

- **Linear** — flip ticket to Done (`mcp__linear__save_issue`; resolve state ID via `mcp__linear__list_issue_statuses` if not cached). Add a comment with the squash SHA if team convention requires it.
- **MEMORY.md** —
  - Move the ticket out of Active Backlog tables.
  - Append squash SHA to any ticket-table entry that tracks it.
  - Add any non-obvious gotcha surfaced during review/fix under "Sticky Technical Conventions" or the right topic file.
  - If Phase 4.5 introduced new convention (e.g. "synthetic probe must align with §F AC") — add to AST-pinned invariants if there's a guard test, or to "Implicit conventions" otherwise.
- **Local repo** — `git fetch --prune && git checkout main && git pull --ff-only`. End on clean main.

## Self-check before completion report

Before writing the user-facing report, confirm:

1. `Skill review-change` was called this turn.
2. `Skill simplify` was called this turn.
3. `Agent(subagent_type="codex:codex-rescue", ...)` was dispatched this turn (or PR was trivial enough that the skill explicitly opted out — note the reason).
4. **Phase 4.25 over-engineering check ran** — aggregate findings were reviewed for cluster signals at least once. If signals fired, the user was prompted with A/B/C and chose; if no signals, this was an explicit no-op (note "no over-engineering signals" in the report).
5. **Phase 4.5 fix loop ran** — every Critical/High/Medium finding from phases 2/3/4 was either fixed in-place or has a documented stop-trigger code (1–8).
6. Verify gate executed real commands AFTER Phase 4.5 fixes.
7. Either a real `gh pr merge ... --squash --delete-branch` ran, OR a stop trigger fired with explicit code.
8. If merged: Linear state was actually flipped AND MEMORY.md actually got an edit (or PR brought zero new gotchas — say so explicitly).

If any check fails, the report is forbidden until you go back and complete the missing step.

## Completion output (zh-tw)

**Default — clean merge, ≤2 lines:**

```
✅ PR #<N> merged: <squash SHA> · Linear NEX-XXX → Done
修了 <N> 個 in-place fix（<one-clause summary>）
```

That's it. The user can `git show <SHA>` if they want detail. They invoked the skill to ship, not to read a report.

**Expand only when one of these occurred:**

- **Codex brought NEW signal that drove a fix** — add 1 bullet naming what Codex caught.
- **Stop trigger fired mid-pipeline** — print the trigger code, the partial state, and the unblock question. No completion-report ceremony.
- **Phase 4.25 cluster signals fired** — print the A/B/C decision and what got dropped/replaced.
- **Verify gate found in-scope failure that's not trivially fixable** — print the failure + partial state.
- **PR is materially complex** (>500 LoC diff, multi-stream ownership, contract change) — at most one short paragraph on the actual risk shape, NOT a section-by-section recap.

Hard rules for output:

- NEVER produce phase-transition narration ("Phase 4.5 complete, here's what I found...").
- NEVER list every finding from review-change / simplify / Codex unless one became a stop-trigger surface.
- NEVER recap verify gate output line-by-line — the lint passed, the merge happened, it's already proof.
- If everything ran clean, the 2-line default IS the report. Resist the urge to embellish.

## Failure

On any phase failure mid-execution: stop, print which phase, the failing artifact, the partial state already applied (Phase 4.5 commits exist? pushed? CI status?), and the minimal unblocking question. Do not auto-retry. Do not silently degrade to manual review. Do not roll back Phase 4.5 commits without explicit user permission.
