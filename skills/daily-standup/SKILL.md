---
name: daily-standup
description: "Turn yesterday's git and Linear activity into a short, plain-language standup Steven pastes into the team channel. Use when the user wants a morning team update — 「standup」/「站立會議」/「今天要貼的進度」/「daily update」. For the multi-day narrative report, use nexrex-weekly-engineering-report instead."
argument-hint: "[window, e.g. 過去三天]"
---

# Daily Standup

Two people read this: engineers, and the team lead, who sometimes relays it onward to sales or
customers. So every line must be skimmable in seconds **and** legible to someone who has never seen
the code. The core move is **白話** — translating mechanism into outcome. Prose and implementation
detail mean the compression has not happened yet.

The team's agreed shape: three sections, **each at most 3 points, descriptions as short as
possible**. Many bugs fixed → ticket numbers only, no descriptions. No relevant progress → skip the
day entirely.

## Defaults

| Setting | Value |
|---|---|
| Author | git email `steven.wu@nexrex.ai` — catches both `Steven Wu` and `steven-wu-nexrex`, and counts work Steven **authored and landed** rather than merely merged |
| Repos | `nr-platform`, `nr-app`, `nr-landing` under `~/Desktop/NexRex/` |
| Window | Yesterday; Monday reaches back to Friday. The bundled script resolves this |
| Language | zh-tw, plain words; English only for product names everyone knows (Garmin, Race Explorer) |
| Voice | First person, Steven's own work |
| Output | Printed inline for copy-paste |

A different window（「過去三天」/「上週五到今天」）is the one thing worth honouring — pass it to the
script as `since` / `until`. Everything else runs on defaults without asking.

## Output template

```
✅ 昨天已完成
- {point 1}
- {point 2}
- {point 3}

🙋 需要幫忙事項
- {point}     ← 沒有就寫「（無）」

🎯 今日重點
- {point 1}
- {point 2}
- {point 3}
```

- **≤3 bullets per section.** More than three and people stop reading. With more than three things,
  select: user-facing > product capability > the rest.
- **A phrase, not a sentence** — something a teammate skims in two seconds
  （`營養追蹤 App+Web Beta 完成`）. One exception: a genuinely user- or product-facing item in
  **昨天已完成** earns a short trailing clause on what it unlocks
  （`賽事資料平台改以新資料庫為準，為支援更多國際賽事打底`）. Internal plumbing and the two
  forward-looking sections stay phrase-length.
- **Bug pile → one roll-up bullet**, ticket numbers only.
- **Every bullet lists every ticket it spans** — `（NEX-A / NEX-B）`, not one representative. Codes
  come from commit subjects or memory; a quick fix with no ticket simply carries none.

## Step 1 — Gather

```bash
bash ~/.claude/skills/daily-standup/scripts/gather-standup-data.sh
```

It fetches each repo (so yesterday's merges show even when local `main` is behind), prints the
resolved window, and per repo lists Steven-authored commit subjects plus a shortstat. Subjects
usually carry the PR number as `(#NNN)`. To confirm a PR is authored rather than merely merged:
`gh pr view <N> --repo NexRex-Dev/<repo> --json author,mergedBy`.

**Complete when** the window is resolved and every commit in it is listed with its repo.

## Step 2 — Enrich from Linear and memory

Git says *what code moved*; Linear and memory say *why it mattered* and *what's next*. Follow the
Linear query discipline — `includeArchived:false`, narrow `updatedAt`, single state, `limit:20`.

- **昨天完成** — `list_issues(assignee:me, state:"Done", updatedAt:"-P3D", includeArchived:false)`.
  A ticket title is already business-framed, making it the best raw material for a 白話 bullet.
  Match it to the `NEX-XXXX` codes in the commit subjects.
- **今日重點** — `list_issues(assignee:me, state:"In Progress", includeArchived:false)`, then
  cross-check against the `Now (...)` section of `MEMORY.md`. Raw Linear "In Progress" carries
  dormant epic shells that memory marks as someone else's; keep only what is genuinely active for
  Steven.
- **需要幫忙** — your own open PRs awaiting review, plus any In-Progress ticket that is `blockedBy`
  something. Memory's blocker / ⚠️ lines are a good source.

Linear MCP unavailable → produce the standup from git and memory, and say ticket enrichment was
skipped.

**Complete when** every commit cluster carries either a matched ticket or an explicit "no ticket".

## Step 3 — Compress, then translate

Where the skill earns its keep. A productive day is 6–14 commits across 2–4 tickets; the format
allows three bullets.

**Compress.** Cluster commits and PRs by shared ticket or user-facing theme — one feature touching
backend and app is **one** bullet spanning both tickets. Rank by who perceives it: user-visible >
product capability being built > internal plumbing > chore. Work no user or PM would recognise does
not earn its own line at standup altitude; fold it into the roll-up as「其他內部優化」. Keep the top
3, collapse the tail.

**Translate.** Engineers narrate the mechanism; the standup narrates the outcome. Lead with the
product or user noun and drop the implementation word entirely.

| Engineer's words | 白話 outcome |
|---|---|
| heal monthly mileage Redis after LWW skips | 月跑量排行榜在某些情況下數字沒更新 → 修好，排行更準 |
| mark Garmin FIT enrichment completion | Garmin 活動不再「資料還沒處理完就先顯示」 |
| complete coach_id reader audit / org-scoped coach resolution | 學員↔教練歸屬切換收尾，聊天會對應到正確的教練 |
| PG → Firestore race projection for Race Explorer | 賽事探索（Race Explorer）開始接上新的賽事資料庫，為支援更多賽事打底 |
| add user label service base eligibility | （內部基礎建設 — 併入「內部優化」或不出現） |

The test: read the bullet aloud to someone who has never seen the code. If they can picture what
changed for a user, it's ready. If they would ask「什麼是 projection / reader audit / Redis？」,
translate again. The `NEX-XXXX` tag rides at the end for anyone who wants to dig; the words before
it stand on their own.

**Complete when** every surviving bullet is free of implementation vocabulary and names a product or
user outcome.

## Step 4 — The forward-looking sections

- **🎯 今日重點 is a forward guess** seeded from In-Progress tickets, open PRs, and memory's `Now`.
  It is a draft the user edits before posting, so emit the bullets plainly with no draft-marker line.
  Same 白話 translation and same dormant-epic filter apply.
- **🙋 需要幫忙 defaults to「（無）」**, filled only from a real blocker or a PR genuinely waiting on
  someone. An empty 需要幫忙 is the normal, honest case.

Git and Linear cannot see customer visits, sales, or meetings; off-git work is the user's to add.

**Complete when** 今日重點 contains only work memory confirms is Steven's and active, and 需要幫忙
reflects a real blocker or reads「（無）」.

## Step 5 — Deliver

Print one fenced copy-paste block. Ticket references stay as bare `（NEX-A / NEX-B）` tags. On a
genuinely bug-heavy day, when the team lead's「票號帶連結」rule applies, expand the roll-up's codes to
full `https://linear.app/nexrex/issue/NEX-XXXX` URLs so Slack unfurls them. Then stop — the user
edits and posts it themselves.

A window with no NexRex-relevant git or Linear activity gets the honest answer rather than padding:
`昨天沒有 NexRex 相關的 commit / ticket 進度 — 依團隊慣例今天可跳過。`

**Complete when** the block is printed inline and every section holds ≤3 bullets.

## Calibration target

Real output, 2026-06-04 — a heavy day: 14 commits across nr-platform and nr-app, ~7 themes, plus
dormant epics polluting Linear "In Progress". Reproduce this altitude.

```
✅ 昨天已完成
- 賽事探索（Race Explorer）開始接上新的賽事資料庫，為支援更多國際賽事打底（NEX-1113 / NEX-832）
- 完成「學員↔教練」歸屬的資料切換收尾，聊天等功能會對應到正確的教練（NEX-1137 / NEX-1126）
- 多項使用者體驗修正與內部優化：月跑量排行榜數字更準（NEX-1146）、Garmin 活動不再顯示不完整（NEX-1145）、教練收件匣群組分流（NEX-1119）；另有顯示一致性與使用者標籤基礎（NEX-1128 / NEX-1105）＋數個小修
```
