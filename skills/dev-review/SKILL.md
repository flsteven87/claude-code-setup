---
name: dev-review
description: Use when reviewing Steven's git contributions over a time period across the NexRex repos (nr-platform / nr-app / nr-landing). Triggers on 'dev review', '開發週報', '開發整理', '回顧這週做什麼', 'review my commits', '幫我整理 X-X 的開發', 'sprint review'. Produces a Traditional Chinese narrative report saved to ~/Desktop by default. Make sure to use this skill whenever the user wants to look back at a stretch of development work — even if they don't say the word "review" — including self-summary, manager updates, performance review material, or recap before status meetings.
---

# Developer Review

Generate a user-impact-driven narrative of Steven's recent development work across the three NexRex repos, with every claim backed by a specific commit / PR / Linear ticket. Output Traditional Chinese, saved to Desktop, framed as a self-summary unless asked otherwise.

## Defaults (don't ask the user about these)

| Setting | Value |
|---|---|
| Author | `Steven Wu` (git author) + `steven-wu-nexrex` (GitHub login) |
| Repos | `~/Desktop/NexRex/nr-platform`, `~/Desktop/NexRex/nr-app`, `~/Desktop/NexRex/nr-landing` |
| Language | Traditional Chinese (zh-tw) |
| Audience | Self (personal summary, no "給主管的觀察" / "executive recommendations" sections) |
| Output path | `~/Desktop/dev-review-steven-{end_date}.md` |
| MEMORY path | `~/.claude/projects/-Users-po-chi-Desktop-NexRex-nr-platform/memory/MEMORY.md` |

If the user explicitly says "給主管" / "manager" / "promo packet" / "team update", switch audience and add the relevant framing (see §Phase E). Otherwise keep the self-summary default.

## What to ask the user

**Only ask about time range.** Examples of acceptable answers: `1w` / `2w` / `1m` / `2026-04-29..2026-05-11` / "上週" / "從 4/29 到今天". Convert relative dates to absolute ISO before running queries.

Don't ask about author, language, repos, or output destination — those are fixed.

## Why this skill exists

A raw `git log` lists commits. A useful weekly recap explains **what the user actually got**, organized by user-facing themes, with traceable backing. The original skill ran git log in one repo and clustered by conventional-commit prefix; in practice this misses three things that matter:

1. **The work spans repos.** A single feature like "locale display context" lands in backend + mobile + web simultaneously. Per-repo views fragment one story into three.
2. **Squash-merged work is invisible in `git log --author`.** The squash commit's author is the merger, not the original developer — need `gh pr list --author` as a parallel data source.
3. **Tickets and ownership decisions live elsewhere.** Linear has the "why this matters" narrative; MEMORY.md has ownership boundaries ("Rex Everywhere = Jeffrey-owned 2026-04-29") and naming-collision warnings.

The phases below address each.

## Phase A — Discover

### A1. Resolve time range

After the user gives the range, convert to absolute ISO dates and confirm by stating them back: "好的，盤點 2026-04-29 → 2026-05-11 共 13 天的開發。"

### A2. Pull data from all three repos in parallel

For each repo run these in **a single message with parallel Bash calls** (use absolute paths, no `cd` per CLAUDE.md):

```bash
# Per-repo git log (catches Steven's authored commits including stacked / unsquashed)
git -C <repo> log --author="Steven Wu" --since="<start>" --until="<end> 23:59" \
    --format="%h|%ad|%s" --date=short --no-merges

# Per-repo shortstat (for the summary stats table)
git -C <repo> log --author="Steven Wu" --since="<start>" --until="<end> 23:59" \
    --shortstat --no-merges
```

### A3. Pull merged PRs (catches squash-merged work git log misses)

```bash
# Auth check — Steven's nr-platform PRs require steven-wu-nexrex account
gh auth status
# If active account is wrong:
gh auth switch --user steven-wu-nexrex

# Per-repo merged PRs (run in parallel across repos)
gh pr list --state merged --limit 100 \
    --json number,title,author,mergedAt,additions,deletions,url \
    --repo NexRex-Dev/<repo-name>
# Then filter mergedAt in window + author.login == "steven-wu-nexrex"
```

### A4. Sanity-check authorship against parallel developers

Critical step — production work happens alongside Jeffrey's parallel ship arcs, and naming clashes are common (e.g. Steven's "athlete insight" vs Jeffrey's "activity insight"). Always pull the full author list in the window for nr-platform:

```bash
gh pr list --state merged --limit 100 --repo NexRex-Dev/nr-platform \
    --json number,title,author,mergedAt
# Filter by window, group by author.login
```

Surface in your internal notes:
- How many PRs each parallel developer shipped in the window
- Any PR titles with semantic overlap to Steven's work (same feature word, adjacent file area)

If you find overlap, **explicitly disambiguate in the report** — e.g. "本主線是 athlete insight（每週 AI 整理），與同期 Jeffrey 在 PR #208 推的 activity insight（每筆活動子類型 prompt eval）是不同 feature。"

### A5. Resolve commits to PRs (for clickable links in the narrative)

For each commit referenced in the final narrative, prefer the merging PR number over the bare hash. The cleanest path:

```bash
gh api repos/NexRex-Dev/<repo>/commits/<sha>/pulls --jq '.[] | "#\(.number)"'
```

If the API returns empty, the commit landed directly on a release branch — note that in the narrative ("2026-MM-DD release branch 直 land") rather than fabricating a PR number.

## Phase B — Enrich

### B1. Read MEMORY.md

Always read it. It usually contains:
- **Ownership decisions** ("Rex Everywhere = Jeffrey-owned since 2026-04-29") — these flag work that should be attributed to Jeffrey even if a Linear ticket assigns it to Steven
- **Locked decisions** (units, timestamps, SSOTs) — these provide the "why" behind seemingly small commits
- **Naming-collision warnings** (`project_naming_collisions_summary_type.md` etc.)
- **Recent ship arcs** — if MEMORY.md was updated within the report window, treat it as authoritative narrative source

### B2. Pull Linear tickets referenced in commits / PRs

Grep commit messages + PR titles for `NEX-\d+`. For each unique ticket:

```
mcp__linear__get_issue(id: "NEX-XXX")
```

Use the ticket title + description to enrich the "why" — Linear holds the business rationale that commit messages omit. If Linear MCP is not authenticated, ask the user to authenticate (this is a one-time cost worth paying).

### B3. Cross-reference release notes

```bash
grep -A 10 "^## \[" /Users/po-chi/Desktop/NexRex/nr-platform/CHANGELOG.md | head -150
```

The CHANGELOG already groups work by version with curated descriptions — use it as a sanity check for major themes, not as the primary narrative source.

## Phase C — Cluster (cross-repo, by user-facing theme)

Cluster the union of commits + PRs from all three repos into **story points based on what changed for the user**, not by conventional-commit prefix or directory. Clustering signals, in priority order:

1. **Shared Linear ticket** — e.g. all PRs / commits mentioning NEX-770 cluster as one story regardless of repo
2. **User-facing capability** — backend SSOT contract + mobile hydration + web display = one cluster ("跨地區顯示語境")
3. **Bug class** — all timezone-correctness fixes are one cluster even if scattered across 6 PRs
4. **Conventional commit scope** — only as a last resort when 1-3 don't apply

For each cluster, label its **dominant narrative shape**:

| Shape | When | Format in Phase D |
|---|---|---|
| User-facing change | Users will perceive the difference (UI, locale, AI text, settings, login flow) | Before/After table |
| System / infra / observability | Internal mechanism change with no direct UI delta | What / Why / Impact prose |
| Tech debt / CI / docs | Engineering velocity improvement | Compact bullet list |

## Phase D — Narrate

### D1. User-facing change clusters → Before/After table

This is the format that the user explicitly preferred over the technical "What/Why/Impact" prose. Make it tangible — every row is a thing a user could actually notice.

```markdown
## 🌏 主線 X：{cluster title from the user's perspective}

{1-2 sentence intro framing why this cluster matters from a user / business angle. Avoid implementation jargon.}

**用戶看到的改變：**

| 之前 | 現在 | 票 / PR |
|---|---|---|
| {what the user saw / experienced before} | {what they see / experience now} | {Linear ticket}：{repo}/{PR link}, {repo}/{commit shorthash} |

**契約 SSOT 建立（讓未來不再回頭）：**

- {ticket}：{repo}/{PR}, {repo}/{PR}
- ...

**附帶清出舊問題：** {if applicable, mention bugs uncovered while doing the main work}
```

Rules for the table:
- Each "之前 / 現在" pair must be **observable** by a user — not "refactored X service" but "活動詳情顯示 UTC 時間 → 用使用者所在時區"
- The 票 / PR column must contain at least one clickable link per row
- Cross-repo PRs in one row are fine and often desirable (shows the feature shipped end-to-end)

### D2. System / infra clusters → What / Why / Impact prose

For observability, deployment, CI, postgres pool work, etc. — users don't see this directly, but the underlying decision matters.

```markdown
## 🛡️ 主線 X：{cluster title}（{NEX-XXX} / {NEX-YYY}）

**背景：** {1-2 sentences — what triggered this work, often an incident or audit finding}

**做了什麼：**
- {behavior change 1}
- {behavior change 2}
- {behavior change 3}

**Backed by：**
- {ticket}：{PR link}({size delta if notable})
- {ticket}：{PR link}
```

### D3. Tech debt / CI / docs → compact bullets

These don't need full prose treatment. Group by epic / ticket cluster, give each item one line.

```markdown
### {Cluster sub-title, e.g. CI Baseline Cleanup（NEX-733 epic — 6 子票收 5）}

**之前：** {one-sentence pain}
**現在：** {one-sentence result}

- {NEX-XXX} {description}：{PR link}
- {NEX-XXX} {description}：{PR link}
- 剩餘：{open child ticket link} {one-line note on what's left}
```

### D4. The 自己的觀察 footer

End the report with a short "自己的觀察" section — 4-6 bullets, each one observation about the period that's hard to derive from git alone. Examples of good observations:

- A theme that emerged unplanned (e.g. "X 並非預設規劃，是在做 Y 過程中陸續挖出來的")
- A workflow that needs investment (e.g. "跨 repo 同步發版目前手動協調，未來會是常態，可考慮 release tooling")
- An ownership / scope note (e.g. "Rex 整合 4/29 已移交 Jeffrey，Linear 上還有 N 張票在我名下要轉出")
- A milestone that's near completion (e.g. "CI baseline 即將完全收網，收完後可移除 close-PR workflow 的中間狀態邏輯")

Don't write "given my recommendations" or "for the manager to decide" — this is Steven's personal summary, not a memo.

## Phase E — Output

### E1. Audience-driven adjustments

| Audience | Tone | Sections to add | Sections to drop |
|---|---|---|---|
| **self** (default) | 自己對自己的整理筆記 | "自己的觀察" footer | "給主管的觀察決策點" / "executive recommendations" |
| manager | 對主管彙報 | "給主管的觀察與決策點", explicit decision points needing sign-off | "自己的觀察" footer |
| team | 對團隊週會 | "影響到誰", coordination items | personal observations |
| promo | 升等 / 績效材料 | 量化 metrics, scope-of-impact 章節 | small ops follow-ups |

Default to **self** unless the user said otherwise. The original skill's "Executive Summary" header is fine for any audience, but the language inside it must match the audience.

### E2. Save the file

Default path: `~/Desktop/dev-review-steven-{end_date}.md`

Why not under `docs/`: self-review reports don't fit any layer in `nr-platform/docs/DOCS_POLICY.md` (it's not architecture / audit / plan / ADR / blog). Putting them in `docs/` would be a governance violation.

If the user explicitly requests `docs/`, check the project's DOCS_POLICY first — if there's no governing policy or the policy permits `docs/reports/`, use that path. Otherwise stay on Desktop.

After writing the file, confirm with the path as a clickable link:
```
已輸出 → [`~/Desktop/dev-review-steven-2026-MM-DD.md`](file:///Users/po-chi/Desktop/dev-review-steven-2026-MM-DD.md)（{lines} 行 / {KB} KB）
```

## Worked Example (from 2026-05-11 run)

Given:
- Window: 2026-04-29 → 2026-05-11
- Source: 42 PRs in nr-platform + 11 PRs in nr-app + 1 PR in nr-landing + 32 unsquashed Steven commits
- MEMORY.md flagged: Rex Everywhere is Jeffrey-owned since 2026-04-29; NEX-782 fixed 99% mobile login failures
- Naming collision detected: Steven's "athlete insight" vs Jeffrey's PR #208 "activity insight"

The narrative produced 3-line摘要, 6 主線 sections, ended with 5-bullet 自己的觀察. Key clusters:

- **跨地區用戶體驗** (NEX-674/761/770/774/730) — user-facing → Before/After table format, spans nr-platform + nr-app
- **NEX-782 mobile login fix** — user-facing but single-thread → mixed prose + commit list
- **Athlete Insight 結構化** — explicitly disambiguated vs Jeffrey's activity insight
- **NEX-569 observability** — system → What/Why/Impact prose
- **NEX-741 agent-readiness** — system → What/Why/Impact prose, includes nr-landing PR #9
- **工程效率（NEX-733 CI baseline, DOCS_POLICY, NEX-700 plan ID, deploy hygiene）** — tech debt → compact bullets per sub-cluster

This is the shape to reproduce. If the next run doesn't match this density / structure given comparable input, something is wrong.

## Common Mistakes (updated from real iterations)

| Mistake | Symptom | Fix |
|---|---|---|
| Only running `git log` | Squash-merged PRs missing from report | Always pull `gh pr list` in parallel |
| Skipping authorship sanity check | Risk of attributing Jeffrey's work to Steven (especially with naming clashes) | Phase A4 — always pull full author list, surface overlaps |
| Per-repo clustering | One feature fragmented into 3 sub-stories | Phase C — cluster cross-repo by Linear ticket / user-facing theme first |
| Default technical categorization (Features / Bugs / Tech Debt) | Report reads like a changelog, not a story | Use Before/After table for user-facing; reserve What/Why/Impact for system work |
| Hardcoded `docs/reports/` output | Violates DOCS_POLICY if project has one | Default to Desktop; only use `docs/` after policy check |
| Including manager-facing decision points by default | Doesn't match self-summary intent | Default audience is `self` — drop "給主管" sections unless asked |
| Listing every commit verbatim | 40+ commits = unreadable | Cluster aggressively; one cluster = one story regardless of commit count |
| Skipping Linear lookup | Reports read shallow — "fixed timezone bug" with no business context | Phase B2 — always enrich `NEX-XXX` references |
| Skipping MEMORY.md | Miss ownership boundaries / naming collisions | Phase B1 — always read it; trust its ownership decisions over Linear assignment |
| Inventing PR numbers for direct-to-main commits | Wrong PR linked or fabricated | Phase A5 — if `gh api .../pulls` returns empty, note "release branch 直 land" honestly |
