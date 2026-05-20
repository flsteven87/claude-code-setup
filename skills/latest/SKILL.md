---
name: latest
description: Pull every source of truth (git, open PRs, Linear, CHANGELOG) up to where it actually is, then rewrite MEMORY.md in place — both syncing drift AND refocusing the file on what the user actually needs as the session opens (current WIP + immediate next step + big locked decisions + load-bearing constraints + 1-3 most recent ships for continuity). The spirit is one word — **latest**. Enforces a hard size target (under 200 lines, where the auto-memory system silently truncates) by extracting off-topic content (older ship history, transient state, reference tables, incident backstory, ops todos) into dedicated topic files. Use when memory has been accumulating across many sessions and may have drifted OR become too verbose, when returning to a project after time away, before a planning session that will lean on memory, when the user types /latest, or when they say '進入最新狀況', '深度更新 memory', '同步最新', 'memory consolidate', 'consolidate memory', 'tidy memory', '清理 memory', 'memory 太雜亂', 'memory 太長', or 'housekeeping'. Replaces and supersedes the older housekeeping skill and goes deeper than catchup — it both fetches truth AND restructures memory. Multi-repo aware (detects sibling repos under a shared parent) and Linear-aware (when the MCP is connected). Runs autonomously end-to-end without asking the user to pick options — applies best-practice judgment, only flagging genuine tensions (Locked Decision contradicted by code, etc.) in the final report.
---

# /latest

Memory drifts. Codebases ship. Tickets close. The job of this skill is one word: **latest**. Pull every source of truth (git, PRs, Linear, CHANGELOG) up to where it actually is, then rewrite MEMORY.md and its sibling memory files to match — so the **current session's** decisions are made from reality rather than stale notes.

**This skill almost always runs at the START of a session, not the end.** Frame all output as "you are about to do work — here is the cleanest starting state", not "you finished work — here is a handoff". The user opens a session, types `/latest`, then immediately moves to planning or coding. Memory and reports should serve that flow.

The output the user cares about: after this skill runs, they can immediately think about what to build next without first having to re-verify what memory claims.

## Autonomy principle

**This skill does not ask the user to pick options.** No focus-filter prompt, no Tier C "approve / reject" gating, no menu of consolidation strategies. The user invoked `/latest` precisely because they want the skill to consolidate using its own best-practice judgment — being asked is the friction they wanted removed.

Apply best-practice judgment end-to-end. When something is genuinely user-owned (a Locked Decision in MEMORY.md contradicted by a recent commit; an architectural invariant whose test was removed), **do not pause and ask** — leave that specific entry untouched and surface it in the final report under "需要你確認的張力" so the user can act on it when they want. The skill keeps moving.

The only auto-executed destructive action that needs surfacing is `gh auth switch` (mutates global gh state); even there, just execute and report — memory or `~/.claude/CLAUDE.md` naming the correct user is sufficient signal.

## Communication language

**All user-facing communication during this skill runs in Traditional Chinese (zh-tw) — including section headers, bullet labels, and template scaffolding, not just prose.** This covers the scope-detection summary in Phase 1, any inline progress notes mid-flow, and the Phase 8 final report.

**English is reserved for technical tokens only:** commit SHAs, PR numbers, ticket IDs (e.g. `NEX-859`), file paths, shell commands, function/variable names, tool invocations, and direct quotes from memory or code. Everything else — including the words around those tokens, the report's own structure, and labels like "Synced" / "Tier C" / "起手就緒" — translates to zh-tw.

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

## What belongs in MEMORY.md (and what doesn't)

This is the **design constraint that drives every edit**. The user's mental model: MEMORY.md is the surface they read at session start — it should answer "what should I do next, and what rules govern that work?" Anything else is a distraction.

The wrong question is "is this fact still true?" The right question is "does the next decision need this fact loaded at session start, or can it be looked up when relevant?" Both are often "true" — only the second belongs.

**Belongs (keep / promote into MEMORY.md):**
- Current WIP + immediate next step (single paragraph; what the user is about to do)
- **Recent ships for continuity** — the 1-3 most recent shipped milestones as **one-line entries each**: `SHA range — title (date) → pointer to ship-summary topic file`. This gives the session narrative context without bloat. Older ships fall out of MEMORY into topic files / `git log`.
- Big locked decisions — the **rule**, not the backstory (one line per decision)
- Load-bearing constraints / invariants (G1–G4-style design principles)
- Scope ownership / guardrails (who owns what, what not to touch)
- Active backlog as one-line signals (Linear has the detail)
- Pointers to topic files (the routing index)
- Session role / per-PR checklist if the user has set one

**Doesn't belong (extract to topic file, or drop entirely):**
- Ship history narrative — multi-paragraph "we did X then Y then Z" prose → CHANGELOG.md, `git log`, and per-ship topic files are the SSOT. Note the exception above: the **1-3 most recent ships stay as one-line entries** for session-opening continuity; this is not the same as ship narrative.
- Ships older than 1-3 sessions — even one-line entries → move to topic file index, drop from the main handoff section
- Transient state — repo HEAD SHAs, cycle dates, open-PR lists older than ~1 week → these go stale within hours; rebuild from `git` / `gh` / Linear at session start
- Per-incident backstory — "NEX-X burned us because [long story]" → extract to a topic file or the lesson into a generalized rule
- Reference tables not consulted every session — three-store ownership, AST invariants list → topic file
- Operational setup info (kubeconfigs, credentials, CLI quirks) → `reference_*.md` files
- Manual ops todo items ("delete orphan HPA", "set env on chat service") → either ticket them, or drop them
- Per-bug records that aren't actively load-bearing → close them or move to a topic file

**Hard size target:** MEMORY.md stays **under 200 lines**. The auto-memory system silently truncates content past line ~200 when loading MEMORY.md into context, so anything past that line (typically the Memory Index, which is critical routing) is invisible to whatever session reads it. This is not a soft preference — it's a correctness constraint. If the file is over 200 lines, extraction to topic files is mandatory, not optional.

**Operational test:** if a section's content is "accurate but I wouldn't read it before deciding what to do next" → it doesn't belong in MEMORY.md regardless of how well-written it is.

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

Report what you found in one or two lines before continuing. The user can interject if you guessed scope wrong (e.g. "no, ignore sibling repo X, it's unrelated") — but **do not stop and ask**. Continue into Phase 2 immediately; the user will interrupt if needed.

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

#### gh credential mismatch — auto-handle

If `git fetch` returns `Repository not found` / `403` for an org repo, it's almost always a **multi-account `gh` / credential-helper mismatch**, not a network problem. Check with `gh auth status`:

- If memory or `~/.claude/CLAUDE.md` names the correct user for this repo, run `gh auth switch --user <named-user>` directly and re-fetch. `gh auth switch` mutates global gh state but is fully reversible; the named user IS the documented best practice, so no need to ask.
- After the switch, before finishing the skill, switch back to whatever account was active originally if it was different — leaving the user pinned to a switched account is the actual hazard.
- If neither memory nor CLAUDE.md names a user: proceed with local-only data (`git log` shows local state regardless), and flag the gap in the final report.

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

⚠️ **Linear filter gotcha**: `list_issues(state: "started")` does not reliably return every In-Progress ticket — observed cases where it returned only epic-shells and missed real WIP children. Always cross-reference with `assignee: me, updatedAt: -P3D` AND, for any ticket MEMORY.md flags as WIP, do a direct `mcp__linear__get_issue` to confirm `statusType` + `startedAt`. Trusting the filter alone has burned this skill before.

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

Build five buckets:

- **Confirmed**: memory matches truth AND belongs in MEMORY.md per the "What belongs" filter → keep
- **Stale-clear**: memory contradicts truth, correct value unambiguous (ticket closed, version bumped, PR merged) → **Tier A auto-edit**
- **Stale-shaped**: memory contradicts truth but the change is structural (entry got longer than needed, three entries describe one shipped thing, "in progress" status flipped) → **Tier B-stale**
- **Off-topic for MEMORY.md**: memory is accurate but the content doesn't belong here per "What belongs in MEMORY.md" — older ship history (beyond 1-3 recent), transient state, reference tables, incident backstory, ops todos → **Tier B-restructure** (extract to topic file, or drop)
- **Tension** (was: Stale-judgment): contradicts a Locked Decision, AST invariant, scope guardrail, or other load-bearing claim → **Tier C report-only**: leave memory unchanged, surface in final report so user can decide later. **Do not pause flow to ask.**
- **Unverified**: no source maps to the claim → leave alone, note low-confidence

Off-topic is the bucket most often missed. Drift-correction makes the memory accurate but doesn't make it focused. After classifying for staleness, do a second pass against the "What belongs" filter and move accurate-but-off-topic content into the Off-topic bucket. **Remember the 1-3-recent-ships exception** — those stay as one-line entries in the handoff section even though they're "ship history".

### Phase 5 — Edit memory (the actual consolidation)

This is the heart of the skill. Apply Tier A → B-stale → B-restructure → C in order. **No tier waits for user approval.** Tier C entries are reported, not gated.

#### Tier A — Auto-edit (mechanical, just do)

Unambiguous, mechanical:

- Update "Current Phase" / "Last Updated" date headers to today's date
- Update "Latest release vX.Y.Z" to actual latest from CHANGELOG/tags
- Remove ticket entries marked **Done in Linear AND** merged-or-closed in git, when older than ~2 cycles
- Fix PR numbers, SHAs, and dates that don't match git
- Remove file-path pointers that are obvious from project structure (e.g. "see `api/v1/endpoints/users.py`" when that's the only users endpoint)
- Merge duplicate entries that cover the same topic
- Collapse ship history entries older than 1-3 sessions into a one-line pointer to topic file / CHANGELOG.md
- Update the handoff "current state" line to reflect actual repo state
- Delete process-artifact memory files (`*-handoff-*.md`, `*-plan-*.md`, `*-implement-*.md`) once the corresponding milestone has shipped — these are workflow scaffolding, not durable memory. **No Tier C ask for these** — they are unambiguously dead post-ship.

#### Tier B-stale — Rewrite outdated entries (apply, list in report)

In-place rewrites of memory that's now wrong-shaped or behind reality:

- Trim oversized entries (>30 lines on one closed ticket) to a 2-line pointer + commit SHA reference
- Rewrite stale "🔴 In Progress" sections to reflect actual state
- Consolidate "open ops follow-up" lists across sessions into one current list — drop items already actioned per git evidence
- Collapse multi-paragraph ship narratives → one-line entry per ship if among 1-3 most recent; pointer to topic file otherwise

No before/after diff needed in the report — list what the entry was about + what it became. The user can `git diff` the memory file themselves if they want byte-level verification.

#### Tier B-restructure — Move content out of MEMORY.md (apply, show destinations in report)

Off-topic content gets extracted, not just trimmed:

- Reference tables / lookup data not consulted every session → topic file (`project_*.md`). If a natural existing topic file exists (e.g. data-store table → `project_data_store_topology.md`), extend it. Otherwise create a new topic file with proper frontmatter.
- Cross-session lessons / ship lessons → `project_cross_session_lessons.md` (or per-milestone ship summary)
- AST invariants / regression-guard tables → `project_ast_invariants.md` (or equivalent)
- Operational setup info → `reference_*.md` files
- Ship summaries beyond the 1-3 most recent → keep their topic files, but drop the in-MEMORY pointer entry from the handoff section (the topic file index still lists them)
- After extraction, MEMORY.md keeps a one-line pointer + a sentence on when to read the topic file

**Report each move explicitly** — destination file path + 1-line summary of what was moved. This is the only "audit trail" the user needs to verify the extraction didn't lose anything.

**Size enforcement is part of B-restructure, not optional.** If after B-stale rewrites the file is still over 200 lines, extraction is required to hit the size target. Don't stop at "I trimmed some" — keep extracting until under budget. **But don't over-extract**: the 1-3 recent ships and load-bearing constraints stay even if it means the file lives at 180 rather than 120 lines.

**Topic-file creation rules:**
- Frontmatter required (`name`, `description`, `type` ∈ {user, feedback, project, reference})
- Filename: `project_<topic>.md` for project facts, `reference_<topic>.md` for setup info, `feedback_<topic>.md` for user preferences
- Add a pointer line in MEMORY.md's Memory Index in the same edit (don't leave orphan files)

#### Tier C — Report tension, never block (do not ask, do not silently rewrite)

A small number of edits would touch genuinely user-owned territory. Do **not** rewrite these silently AND do **not** stop and ask. Leave the memory entry untouched and surface the tension in the Phase 8 report.

Tension cases:

- A Locked Decision in MEMORY.md whose direct opposite was just committed
- An AST-pinned invariant whose underlying test was removed in a recent commit
- A scope guardrail ("X is owned by Person Y") where commits show ownership has moved
- Session Role / collaboration-style entries the user wrote in first person — never rewrite
- Architectural invariants whose contradicting evidence is a single commit (one commit isn't enough to overturn a deliberate locked rule)

For each tension, the Phase 8 report shows:
- Quoted memory text
- Evidence of contradiction (commit SHA, missing test path, etc.)
- A one-line "我會建議：…" — but no action taken

The user reads the report at their pace and decides. The skill is done.

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

### Phase 7 — Sibling-artifact sweep (light pass)

Quick scan only — this is residual housekeeping, not core skill value. If nothing's obvious in 30 seconds, skip and move on.

- **`.bak` files older than 7 days** left over from prior cleanups → delete (announce, don't ask)
- **Completed plan files** under `specs/`, `plans/`, `.claude/plans/`: only flag candidates in the report (every checkbox checked, no `TODO`/`PENDING`/`IN PROGRESS` strings). **Don't auto-delete** — plan files often have context the user wants to reference even after completion
- **CLAUDE.md size**: if `~/.claude/CLAUDE.md` >250 lines, surface candidates for extraction to `~/.claude/rules/` as a suggestion. **Don't auto-edit** — CLAUDE.md is user-style, owned by the human
- **Worktrees** already covered if Phase 2 invoked `git-state-audit`

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

### MEMORY.md 體積
- 編輯前：<N> 行 / <KB>
- 編輯後：<N> 行 / <KB>（目標 < 200 行）

### Memory 編輯 — Tier A + B-stale（已套用）
- ✅ <一句話描述> — 依據：<SHA | PR# | ticket | 日期>
- ✅ <一句話描述> — 依據：<...>

### Memory 編輯 — Tier B-restructure（已搬家）
- 📦 <內容主題> → [`destination_file.md`](destination_file.md)（一句話說明搬了什麼）
- 📦 <內容主題> → [`destination_file.md`](destination_file.md)（...）

### 需要你確認的張力（已記錄但未動）
- 🟡 Locked Decision「X」被 commit <SHA> 直接違反 — memory 未動，我建議：<...>
- 🟡 AST guard「Y」對應的測試在 <SHA> 被移除 — memory 未動，我建議：<...>

### Linear 建議（請你手動處理）
- NEX-X：Linear 顯示 In Progress，但 PR 三天前已 merge — 建議改 Done
- NEX-Y：memory 把它列為下個優先，Linear 卻顯示 Cancelled

### 起手就緒
<一段 2–3 句：你現在實際在哪、立刻可動的下一步、有沒有 blocker。>
```

收尾那段（「起手就緒」）是真正的 deliverable，其他都是 audit trail。兩三句，不超過。把它當成「session 第一個 todo 寫好給你」，不是「下次再來看」。

**「已搬家」段不是裝飾**：它讓用戶 30 秒內驗證 extraction 沒漏掉重要內容、知道下次去哪找。若本輪沒搬家就省略整段；若搬了，每個 destination 要附上一行說明搬了什麼。

**「需要你確認的張力」段是純資訊**：不是 todo 清單、不是阻塞點。即使這段有條目，「起手就緒」段照樣寫 — 用戶可以選擇先動手再回頭看張力，也可以先處理張力。skill 不替用戶決定順序。

## Risk discipline

- **Memory edits are not destructive when made carefully.** Don't apologize for editing. The Tier system separates "just do it" (A/B) from "report tension, don't touch" (C).
- **But don't rewrite what you don't understand.** Memory often encodes invariants that took a session of debugging to learn. Deleting an entry because it looks unverified is worse than leaving a stale one. When in doubt, leave alone and flag in the report.
- **Whole-file deletion is OK for two cases only**: (1) process-artifact files (`*-handoff-*.md`, `*-plan-*.md`, `*-implement-*.md`) once the corresponding milestone has shipped — these are dead workflow scaffolding; (2) topic files whose entire content has been folded into another file. Both are Tier A — just do, report. Never wipe a section of a load-bearing file.
- **Cite evidence in your edits.** Every Tier A/B item in the report must point to a SHA, PR #, ticket ID, or date. Every Tier C tension must point to the contradicting evidence. The user should be able to verify any line of the report without re-running anything.

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
| Auto-deleting "Locked Decisions" because a recent commit contradicts them | Don't rewrite locked decisions silently AND don't ask. Leave the entry as-is, flag the tension in Tier C report section. |
| Asking the user to pick options mid-flow | This skill runs autonomously. No focus filter prompt, no Tier C approval gate, no menu of strategies. If the user invoked `/latest`, they want best-practice judgment applied, not to be polled. |
| Pulling `main` on a sibling repo the user isn't actively in | Fetch is enough. `pull` mutates that repo's state without user context. |
| Writing a wall-of-text report | Lean on the template. The "起手就緒" paragraph is what the user reads; the rest is for audit. |
| Running this skill when the user actually wanted `catchup` | `catchup` is read-only, 30 seconds. This is write, 2–5 minutes. If user seems to want fast context, ask. |
| Skipping Phase 1 scope detection | Easy to assume single-repo and miss sibling repos with relevant state. |
| Framing the closing summary as "next session" | This skill runs at session START. The closing line tells the user what they're about to do, not what some future-them will do. Use "起手就緒" / "立刻可動", not "下次 session". |
| Stripping ship continuity entirely | "Doesn't belong" → ship history narrative. "Belongs" → 1-3 most recent ships as one-line entries. Don't be so aggressive that the session opens with zero context of what just landed. |
| Editing topic files but not updating their YAML frontmatter | `description` is what the auto-memory system uses to decide relevance. Out-of-sync frontmatter = silently-misfiled memory. |
| Trying to fix Linear ticket state from this skill | Out of scope. Propose in the report, the user actions. |
| Asking before `gh auth switch` when memory names the right user | Memory or CLAUDE.md naming the user IS the documented best practice. Switch, fetch, switch back. Just do. |
| Phase 8 report leaving section headers / bullet labels in English ("Synced", "Memory edits — Tier A+B") | Violates the Communication language rule. Headers and labels are zh-tw too; only technical tokens (SHA, PR#, ticket ID, file path, command) stay English. |
| Tier B framing every restructure as "show diff" | Narrative rewrites don't have a meaningful before/after diff. Report what each entry was about and what it became; the user can `git diff` if they need byte-level audit. Use the explicit "已搬家" report section for extractions. |
| Trusting `mcp__linear__list_issues(state: "started")` filter alone | The filter has missed real WIP children in past runs. Cross-reference with `assignee: me + updatedAt: -P3D` AND direct `get_issue` on every ticket MEMORY.md flags as WIP. |

## Output Principle

**Focus over completeness — MEMORY.md is a tool for the immediate next decision, not a project journal.** Every entry should answer "would I read this before deciding what to do in the next 30 minutes?" If the answer is "only if I happened to be working on that specific surface" → topic file, not MEMORY.md. **Exception**: 1-3 most recent ships stay as one-line entries for session-opening continuity — they earn their place by being what the user usually wants to remember they just did.

**Autonomy over consultation — `/latest` does not ask the user to drive.** If a choice is value-neutral (which file gets a topic-file extraction, whether to drop a stale follow-up) → just make it. If a choice is genuinely user-owned (rewriting a Locked Decision) → don't make it, don't ask either, report it in Tier C and keep moving.

**Evidence first, edit second, narrative third.** Every Tier A/B edit must be traceable to a git/Linear/CHANGELOG fact, or to the "What belongs" filter for off-topic moves. Every Tier C tension must show its evidence. The closing "起手就緒" paragraph must be derivable from the synced state, not from memory you just edited.
