---
name: latest
description: Pull every source of truth (git, open PRs, Linear, CHANGELOG) up to where it actually is, then rewrite MEMORY.md in place so the next decision is made from reality rather than stale notes. The spirit is one word — **latest**. Use when memory has been accumulating across many sessions and may have drifted, when returning to a project after time away, before a planning session that will lean on memory, when the user types /latest, or when they say '進入最新狀況', '深度更新 memory', '同步最新', 'memory consolidate', 'consolidate memory', 'tidy memory', '清理 memory', or 'housekeeping'. Replaces and supersedes the older housekeeping skill and goes deeper than catchup — it both fetches truth AND writes memory. Multi-repo aware (detects sibling repos under a shared parent) and Linear-aware (when the MCP is connected). Stops to ask only when edits would rewrite locked decisions, architectural invariants, or other high-controversy content.
---

# /latest

Memory drifts. Codebases ship. Tickets close. The job of this skill is one word: **latest**. Pull every source of truth (git, PRs, Linear, CHANGELOG) up to where it actually is, then rewrite MEMORY.md and its sibling memory files to match — so the user's next decision is made from reality rather than stale notes.

The output the user cares about: after this skill runs, they can immediately think about what to build next without first having to re-verify what memory claims.

## Communication language

**All user-facing communication during this skill runs in Traditional Chinese (zh-tw) — including section headers, bullet labels, and template scaffolding, not just prose.** This covers the scope-detection summary in Phase 1, any 🟡 ask-once prompts (e.g. `gh auth switch` confirmation, Tier C proposals), and the Phase 8 final report.

**English is reserved for technical tokens only:** commit SHAs, PR numbers, ticket IDs (e.g. `NEX-859`), file paths, shell commands, function/variable names, tool invocations, and direct quotes from memory or code. Everything else — including the words around those tokens, the report's own structure, and labels like "Synced" / "Tier C" / "Next session is ready" — translates to zh-tw.

If the user explicitly asks for English mid-flow, switch; otherwise keep zh-tw as the default for this skill specifically (even if other skills in the same session use English). "Headers help skimming" is NOT a license to leave them in English — Chinese headers skim just as well for a zh-tw user, and mixed-language output is the louder smell.

## When this is the right tool

Use when ANY of:
- Memory hasn't been touched in 3+ sessions and you suspect drift
- User says "進入最新狀況", "consolidate memory", "深度更新 memory", or anything in the description trigger list
- Returning to a project after >1 week away
- Before a planning session where you'll lean on memory to choose direction

**Not** the right tool for:
- Quick context rebuild → use `catchup` (read-only, 30 seconds)
- Just cleaning git state → use `git-state-audit`
- A brand-new project with no memory yet — skip, there's nothing to consolidate

## Workflow (sequential phases)

Each phase consumes the output of the previous one. Don't reorder. Phases 1–4 gather evidence; Phase 5 is where memory actually gets written; Phase 6–8 wrap up.

### Phase 1 — Detect scope

Before reading or editing anything, figure out what we're consolidating against:

1. **Project root**: `git rev-parse --show-toplevel` from the user's working directory.
2. **Memory location**: usually `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`. The encoded path replaces `/` with `-`. List the whole memory directory — there will be sibling `.md` files referenced from MEMORY.md.
3. **Sibling repos**:
   - Walk up one directory from project root and `ls` for sibling git repos.
   - Cross-check MEMORY.md for repo names that aren't the current one.
   - If found → treat as multi-repo. Otherwise single-repo.
4. **Ticket system**: scan MEMORY.md for ticket-ID patterns (`[A-Z]+-\d+`). The dominant prefix tells you the Linear team.
5. **Linear availability**: check whether `mcp__linear__*` tools are loaded. If not, the Linear phases become best-effort — note as a gap, don't ask the user to authenticate unless they bring it up.

Report what you found in one or two lines before continuing. The user should be able to redirect if you guessed scope wrong (e.g. "no, ignore sibling repo X, it's unrelated").

### Phase 2 — Sync git truth

For the primary repo:

```bash
git fetch --all --prune --tags
git status -sb
git log --oneline -20 origin/main
git tag --sort=-v:refname | head -5
```

If the primary repo is on `main` AND working tree clean AND behind `origin/main` → `git pull --ff-only origin main`.

If anything else (different branch, uncommitted changes, divergence) → **invoke the `git-state-audit` skill in default mode**. Don't replicate its logic here; it owns this concern, including the WIP-triage A/B/C/D pattern, rebase handling, and worktree cleanup.

For each sibling repo: `git fetch` only. Don't `git pull` repos the user isn't actively in — fetching is enough to verify memory claims; pulling mutates state the user may not want touched right now.

#### gh credential mismatch — 🟡 ask once

If `git fetch` returns `Repository not found` / `403` for an org repo, it's almost always a **multi-account `gh` / credential-helper mismatch**, not a network problem. Check with `gh auth status`:

- If memory or `~/.claude/CLAUDE.md` names the correct user for this repo (e.g. `gh auth switch --user <org-user>`), surface that command and **ask once** before running it. `gh auth switch` mutates global state and can stash the wrong user mid-flow elsewhere — don't run it silently even though "memory predicted it".
- After the user OKs, run the switch, re-fetch, and continue.
- If the user declines: proceed with whatever local-only data is available (`git log` shows local state regardless), and flag the gap in the final report.

This is the one git-side action in this skill that's NOT auto-execute. Everything else in Phase 2 is either read-only or `git-state-audit`'s problem.

After sync, capture:
- Latest 20 commits on `main` per repo (SHA + subject)
- Current branch, ahead/behind counts
- Any worktrees still in use

### Phase 3 — Sync PR & ticket truth

**PRs (via `gh`)**:
```bash
gh pr list --state open --limit 30 --json number,title,author,headRefName,createdAt
gh pr list --state merged --limit 30 --search "merged:>$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)" --json number,title,mergedAt,author
```
For multi-repo, use `gh -R <owner/repo>` per repo. Tag which PRs are user-owned vs others (compare against `gh api user --jq .login`).

**Linear (if MCP available)**:
- Active cycle for the detected team: `mcp__linear__list_cycles`, filter by current dates
- Open issues assigned to the user: `mcp__linear__list_issues` with `assignee: me, state.type ∈ {started, unstarted}`
- Recently completed (last 14 days): `mcp__linear__list_issues` with `state.type: completed, updatedAt: ->14d`
- Spot-check individual fetches for any ticket ID prominent in MEMORY.md whose state would change the memory entry

**CHANGELOG**: read the top of `CHANGELOG.md` if present — capture the most recent released version and the unreleased section header.

### Phase 4 — Cross-reference memory against truth

Read MEMORY.md and every sibling memory file in the same directory. For every concrete claim, classify:

| Claim type | Verification |
|---|---|
| "Latest release vX.Y.Z" | CHANGELOG top + `git tag --sort=-v:refname` |
| "PR #N merged as SHA" | `gh pr view <N>` and `git log --grep` |
| "Ticket X is Done / In Progress" | `mcp__linear__get_issue` |
| "X file lives at path Y" | `ls`/`find` |
| "Function F implements behavior Z" | `grep` — only if recent and load-bearing |
| Dated entries ("Current Phase: <date>") | today's date vs the date in memory |
| "Person P owns area A" | hard to verify mechanically — leave alone unless commits flatly contradict |

Build four buckets:

- **Confirmed**: memory matches truth → keep
- **Stale-clear**: memory contradicts truth, correct value unambiguous (ticket closed, version bumped, PR merged) → **Tier A auto-edit**
- **Stale-shaped**: memory contradicts truth but with shape change (entry got longer than needed, three entries describe one shipped thing, "in progress" status flipped) → **Tier B edit-with-diff-shown**
- **Stale-judgment**: contradicts a Locked Decision, AST invariant, scope guardrail, or other load-bearing claim → **Tier C propose-only**
- **Unverified**: no source maps to the claim → leave alone, note low-confidence

### Phase 5 — Edit memory (the actual consolidation)

This is the heart of the skill. Apply edits in **decreasing safety order**, so the user sees Tier A progress before Tier C decisions land.

#### Tier A — Auto-edit (no prompt, just do it and list in the report)

Unambiguous, mechanical:

- Update "Current Phase" / "Last Updated" date headers to today's date
- Update "Latest release vX.Y.Z" to actual latest from CHANGELOG/tags
- Remove ticket entries marked **Done in Linear AND** merged-or-closed in git, when older than ~2 cycles
- Fix PR numbers, SHAs, and dates that don't match git
- Remove file-path pointers that are obvious from project structure (e.g. "see `api/v1/endpoints/users.py`" when that's the only users endpoint)
- Merge duplicate entries that cover the same topic
- Collapse repeated "ship history" entries into a one-line pointer to CHANGELOG.md
- Update working-memory "next session pickup" line to reflect actual current state

#### Tier B — Edit with diff shown (apply, but display before/after in the report)

Shape changes; user wants to see what happened:

- Trim oversized entries (>30 lines on one closed ticket) to a 2-line pointer + commit SHA reference
- Rewrite stale "🔴 In Progress" sections to reflect actual state
- Consolidate "open ops follow-up" lists across sessions into one current list — drop items already actioned per git evidence
- Tighten the MEMORY.md index when it exceeds its size budget (the auto-memory system truncates after ~200 lines) — extract heavy content into separate topic files
- Promote repeated facts up to MEMORY.md, or push detail down into topic files, depending on where it belongs

#### Tier C — Propose only (ask user per item, don't write)

These edits require human judgment because the **why** behind them doesn't decay just because the **what** changed:

- Edits to "Locked Decisions" / "Load-Bearing Constraints" / architectural invariants
- Removing AST-pinned invariants or test-backed contracts — first verify the test still exists; if it does, the memory entry is still load-bearing and the contradiction is in code
- Rewriting "Session Role" or collaboration-style entries — these are user-style, not project-state
- Edits to scope guardrails ("X is owned by Person Y", "don't reopen Z without gate G") unless git evidence flatly contradicts ownership
- Removing entries that read like incident post-mortems — the value is the lesson, not the date

For each Tier C item, show:
- Current memory text (quoted)
- Evidence suggesting it's stale (commit SHA, ticket state, etc.)
- Proposed replacement, or "delete"
- One-line argument

Then wait for a per-item OK. Don't batch.

#### Memory-file mechanics

The auto-memory system uses a specific format:
- Each topic file has YAML frontmatter (`name`, `description`, `type` ∈ {user, feedback, project, reference})
- `MEMORY.md` is an **index only** — one line per pointer, no body content
- Frontmatter `name` / `description` must stay in sync with the body content

When you edit:
- Per-file edits → use `Edit` tool, preserve frontmatter
- Splitting one topic file into two → write new files with full frontmatter, then add pointer lines to MEMORY.md, then remove the old file
- Never write memory content directly into MEMORY.md — push it into a topic file with a pointer

If a topic file's `description` no longer matches its content after your edits, update the frontmatter too.

### Phase 6 — Propose Linear updates (do not execute)

This skill does **not** modify Linear. But if cross-referencing surfaced state mismatches, list them:

- "NEX-X marked In Progress in Linear but its PR merged 3 days ago — propose moving to Done"
- "NEX-Y appears in MEMORY.md as next priority but Linear shows Cancelled — already removed from memory; you may want to re-prioritize the queue"

Frame these as suggestions for the user to action themselves. Linear changes are visible to the team and have side effects (notifications, cycle accounting, manager dashboards) — they need explicit human decision and shouldn't surprise teammates.

### Phase 7 — Sibling-artifact sweep (former housekeeping scope)

Now that memory is consolidated, do the lighter cleanup the old `housekeeping` skill covered:

1. **Completed plan files** under `specs/`, `plans/`, `.claude/plans/`: if every checkbox is checked and no `TODO`/`PENDING`/`IN PROGRESS` strings remain → delete (announce in report, don't ask)
2. **Stale `.claude/worktrees/`** orphans → already covered if Phase 2 invoked `git-state-audit`; otherwise spot-check
3. **CLAUDE.md size**: if global `~/.claude/CLAUDE.md` is >250 lines, surface candidates for extraction to `~/.claude/rules/` — but **don't auto-edit** (CLAUDE.md is user-style, owned by the human)
4. **`.bak` files older than 7 days** left behind by previous cleanup runs → delete

### Phase 8 — Report

Output entirely in **Traditional Chinese (zh-tw)** per the Communication language section above — section headers, bullet labels, scaffolding, all of it. Only technical tokens (SHA, PR #, ticket ID, file path, command) stay English. Use this template; keep it scannable, the user shouldn't have to read prose:

```
## Memory 同步報告 — <YYYY-MM-DD>

### 已同步
- 主 repo：<name> @ <branch>，落後 origin/main <N> / 領先 <M>
- 兄弟 repo：<list，或「無」>
- 開放中 PR：總共 <total>，自己手上 <user-owned>
- Linear：Cycle <N> 進行中，自己 <X> 個 in-progress，過去 14 天完成 <Y> 個
- 最新發佈：v<X.Y.Z>

### Memory 編輯 — Tier A+B（已套用）
- ✅ <一句話描述> — 依據：<SHA | PR# | ticket | 日期>
- ✅ <一句話描述> — 依據：<...>
- ✅ <一句話描述> — 依據：<...>

### Tier C — 等你裁示
- 🟡 Locked Decision「X」似乎被 commit <SHA> 違反。保留 / 更新 / 移除？
- 🟡 AST guard「Y」指向 <path> 的測試 — 該測試在 <SHA> 被移除。調查 / 移除？

### Linear 建議（請你手動處理）
- NEX-X：Linear 顯示 In Progress，但 PR 三天前已 merge — 建議改 Done
- NEX-Y：memory 把它列為下個優先，Linear 卻顯示 Cancelled

### 下次 session 就緒
<一段 2–3 句的 handoff：你現在實際在哪、最明顯的下一步是什麼、什麼事卡在誰身上。>
```

收尾那段（「下次 session 就緒」）是真正的 deliverable，其他都是 audit trail。兩三句，不超過。

## Risk discipline

- **Memory edits are not destructive when made carefully.** Don't apologize for editing. The Tier system is exactly there to separate "just do it" from "ask".
- **But don't rewrite what you don't understand.** Memory often encodes invariants that took a session of debugging to learn. Deleting an entry because it looks unverified is worse than leaving a stale one. When in doubt, leave alone.
- **Never delete a whole memory file or wipe a whole section.** Always edit at the bullet / paragraph / pointer-line level. If a file is genuinely obsolete, propose deletion in Tier C with the topic-file removal as a single proposal.
- **Cite evidence in your edits.** Every Tier A/B item in the report must point to a SHA, PR #, ticket ID, or date. The user should be able to verify any line of the report without re-running anything.

## Multi-repo handling

If sibling repos detected:

- Phase 2: `fetch` on each, `pull` only on the primary (and only if clean + on main + behind)
- Phase 3: PR sync on each via `gh -R <owner/repo>`
- Phase 4: cross-reference includes claims about any of the repos — memory often says "in repo-A we did X, in repo-B Y is pending"
- Phase 5: memory is single-file (MEMORY.md indexes everything) but contains entries from all repos; the Tier classification still applies per entry, regardless of which repo it's about
- Phase 8: list each repo on its own "Synced" line

## When Linear MCP is unavailable

Common case: user hasn't authenticated this session. Phases that need Linear become best-effort:

- Phase 1 still detects the team from ticket-prefix patterns
- Phase 3 skips Linear, PR sync still runs
- Phase 4 cross-references against git/PR/CHANGELOG only — flag ticket-state claims as "unverified (Linear offline)" and leave them untouched
- Phase 6 emits: "Linear sync skipped — run `mcp__linear__authenticate` and rerun if you need ticket cross-check"
- Tier A/B edits proceed for everything that doesn't depend on Linear state. Tier C is unaffected (it was always conservative).

Don't ask the user to authenticate mid-flow unless they bring it up — a partial run is still valuable.

## Common mistakes

| Mistake | Fix |
|---|---|
| Treating MEMORY.md as authoritative and editing code/tickets to match it | Memory is downstream of code/git/Linear. When they conflict, memory loses. |
| Auto-deleting "Locked Decisions" because a recent commit contradicts them | The decision may need revisiting, but that's a human conversation. Propose, don't delete. |
| Pulling `main` on a sibling repo the user isn't actively in | Fetch is enough. `pull` mutates that repo's state without user context. |
| Asking permission for every Tier A edit | The whole point of this skill is to absorb state-syncing toil. If the edit is unambiguous, just do it and list it. |
| Writing a wall-of-text report | Lean on the template. The closing paragraph is what the user reads; the rest is for audit. |
| Running this skill when the user actually wanted `catchup` | `catchup` is read-only, 30 seconds. This is write, 2–5 minutes. If user seems to want fast context, ask. |
| Skipping Phase 1 scope detection | Easy to assume single-repo and miss sibling repos with relevant state. |
| Rewriting "next session pickup" from memory you just edited | The closing summary must be derivable from the **synced state**, not from notes you wrote 30 seconds ago. |
| Editing topic files but not updating their YAML frontmatter | `description` is what the auto-memory system uses to decide relevance. Out-of-sync frontmatter = silently-misfiled memory. |
| Trying to fix Linear ticket state from this skill | Out of scope. Propose, the user actions. |
| Running `gh auth switch` without asking when fetch 403s | 🟡 — same risk pattern as `git-state-audit`. Surface command, ask once, then run. Don't rely on memory predicting the switch as license to auto-execute. |
| Phase 8 report leaving section headers / bullet labels in English ("Synced", "Memory edits — Tier A+B", "Next session is ready") | Violates the Communication language rule. Headers and labels are zh-tw too; only technical tokens (SHA, PR#, ticket ID, file path, command) stay English. "Headers help skimming" is a rationalization — Chinese headers skim just as well. |

## Output Principle

**Evidence first, edit second, narrative third.** Every Tier A/B edit must be traceable to a git/Linear/CHANGELOG fact. Every Tier C proposal must show its evidence. The closing "next session is ready" paragraph must be derivable from the synced state, not from memory you just edited.
