---
name: daily-standup
description: Use when Steven needs a short daily standup / morning team-channel update — reviewing yesterday's work (git + Linear across nr-platform / nr-app / nr-landing) and drafting today's focus. Produces an ultra-short, copy-paste-ready Traditional Chinese update with three sections (✅ 昨天已完成 / 🙋 需要幫忙事項 / 🎯 今日重點), max 3 plain-language bullets each, written for a non-technical reader. Triggers on '/daily-standup', 'standup', '站立會議', '每日更新', '寫今天要貼的進度', '同步昨天進度', '早上 update', 'daily update', '今天的 standup', or any time the user wants a brief morning team sync. This is the SHORT daily version for pasting into a chat channel — for the heavyweight multi-day narrative report, use dev-review instead. Make sure to use this skill whenever the user wants a quick daily team-channel update even if they don't say the word 'standup'.
---

# Daily Standup

Turn yesterday's git + Linear activity into a **very short, business-readable** standup the user pastes into the team channel each morning. Two people read it: engineers, and non-engineers (the team lead, who sometimes relays it onward to sales or customers). So every line must (a) be skimmable in seconds and (b) make sense to someone who has never seen the code. A long technical report defeats both. If you're writing prose or implementation detail, you've already failed — compress harder and translate to plain outcomes.

This is the daily, disposable counterpart to `dev-review` (the long multi-day narrative saved to Desktop). Never produce a `dev-review`-shaped wall here.

## The brief the user is mirroring

The team agreed on this shape (from the team lead): three sections — 昨天完成 / 今日重點 / 需要幫忙 — **each at most 3 points, descriptions as short as possible.** If many bugs were fixed, just list ticket numbers, no description. Skip the whole thing if there was no relevant progress that day. The user picked the team lead's exact section order: ✅ 昨天 → 🙋 幫忙 → 🎯 今日.

## Defaults — don't ask about these

| Setting | Value |
|---|---|
| Author | git email `steven.wu@nexrex.ai` (catches both `Steven Wu` and `steven-wu-nexrex`). This counts work Steven **authored and landed** — not PRs he merely clicked merge on, which is the right meaning for a standup. |
| Repos | `nr-platform`, `nr-app`, `nr-landing` under `~/Desktop/NexRex/` |
| Window | **Yesterday** (today reviewing yesterday). If today is Monday, reach back to Friday to cover the weekend. The bundled script handles this. |
| Language | Traditional Chinese (zh-tw), plain words; English only for product names everyone knows (e.g. Garmin, Race Explorer) |
| Voice | First person, Steven's own work (like the team lead's example) |
| Output | Printed **inline** for copy-paste — never save a file (no scratch files) |

The only thing worth honouring if the user says it: a different window ("過去三天" / "上週五到今天"). Pass it to the script as `since` / `until` args. Otherwise run with no args.

## Output template — reproduce this exactly

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

Hard rules, because they're the team's agreement and the reason the format works:
- **Plain business language, not jargon — the most important rule.** Every bullet must be legible to a *non-engineer*: say what changed for the user or the product, never the mechanism. `月跑量排行榜數字更準` — not `monthly mileage Redis LWW-heal`. The translation discipline is Step 3, and it's where most of the value is.
- **≤ 3 bullets per section.** More than three and people stop reading. If you have more than three things, you're not selecting — pick the three that matter most (user-facing > product capability > the rest).
- **Short outcome, not a sentence — but business-facing 昨天已完成 items earn a little more.** Default is a phrase a teammate skims in two seconds (`營養追蹤 App+Web Beta 完成`, not `我今天完成了營養追蹤功能的 App 和 Web 版本`). The one exception: in **昨天已完成**, a genuinely user/product-facing ticket may carry a short trailing clause on *why it matters or what it unlocks* — one extra breath, not a sentence (`賽事資料平台改以新資料庫為準，為支援更多國際賽事打底`, not just `賽事資料平台上線`). This allowance is **only** for business-facing completed work; internal plumbing stays a terse roll-up, and 今日重點 / 需要幫忙 stay phrase-length.
- **Bug pile → one bullet.** Many small fixes collapse into a single roll-up bullet, ticket numbers only, no per-bug description.
- **List every ticket a bullet spans.** One user-facing bullet usually clusters several PRs across repos and several tickets — show them all as `（NEX-A / NEX-B）`, not just one representative, and the roll-up bullet carries the whole set of codes it covers. Only cite codes you can actually source (commit subject/body, or memory); a quick fix with no ticket simply gets none — never invent a code.

## Step 1 — Gather yesterday's facts

Run the bundled script (it fetches each repo so it sees yesterday's merges even when local `main` is behind, then logs Steven-authored commits in the window):

```bash
bash ~/.claude/skills/daily-standup/scripts/gather-standup-data.sh
```

It prints the resolved window and, per repo, the commit subjects + a shortstat. Commit subjects usually already carry the PR number as `(#NNN)`. You rarely need `gh` — but if you want to confirm a PR is genuinely Steven's authored work (not one he just merged for someone else), `gh pr view <N> --repo NexRex-Dev/<repo> --json author,mergedBy` settles it.

## Step 2 — Enrich from Linear + memory

Git tells you *what code moved*; Linear and memory tell you *why it mattered to the product* and *what's next*. Pull these (follow the Linear query discipline — `includeArchived:false`, narrow `updatedAt`, single state, `limit:20`):

- **For 昨天完成** — `list_issues(assignee:me, state:"Done", updatedAt:"-P3D", includeArchived:false)`. A ticket's title is already business-framed — it's the best raw material for a plain-language bullet. Match it to the `NEX-XXXX` codes in the commit subjects.
- **For 今日重點** — `list_issues(assignee:me, state:"In Progress", includeArchived:false)`. These are the honest candidates for "today". **But raw Linear "In Progress" includes dormant epic shells** (e.g. Rex Everywhere epics that memory marks as someone else's) — cross-check the **`Now (...)` section of MEMORY.md** and keep only what's genuinely active for Steven.
- **For 需要幫忙** — your own open PRs awaiting review, plus any In-Progress ticket that's `blockedBy` something. Memory's blockers/⚠️ lines are a good source.

If Linear MCP isn't connected, don't block — produce the standup from git + memory and note that ticket enrichment was skipped.

## Step 3 — Compress, then translate to business language

This is where the skill earns its keep, and it's two moves.

**First, compress.** A productive day is 6–14 commits across 2–4 tickets; the standup allows three bullets. So cluster, then select:

1. Cluster commits/PRs by shared Linear ticket or user-facing theme (one feature that touched backend + app = **one** bullet, not three — but that bullet then lists *all* the tickets it spans, e.g. `（NEX-1113 / NEX-832）`).
2. Rank by who-perceives-it: a user-visible change > a product capability being built > internal plumbing > chore. At standup altitude, **purely internal work that no user or PM would recognise usually doesn't earn its own line** — let it fold into the roll-up as "其他內部優化", or drop it.
3. Keep the top 3. Collapse the tail into one roll-up bullet.

**Then translate — the move the team lead explicitly asked for.** Engineers narrate the *mechanism*; the standup must narrate the *outcome*. Rewrite every surviving bullet so a non-technical teammate (or a customer the lead is briefing) understands what got better, with zero codebase knowledge. Lead with the product/user noun, not the system noun. Delete the implementation word entirely.

| Engineer's words (don't ship this) | Plain outcome (ship this) |
|---|---|
| heal monthly mileage Redis after LWW skips | 月跑量排行榜在某些情況下數字沒更新 → 修好，排行更準 |
| mark Garmin FIT enrichment completion | Garmin 活動不再「資料還沒處理完就先顯示」 |
| complete coach_id reader audit / org-scoped coach resolution | 學員↔教練歸屬切換收尾，聊天會對應到正確的教練 |
| PG → Firestore race projection for Race Explorer | 賽事探索（Race Explorer）開始接上新的賽事資料庫，為支援更多賽事打底 |
| add user label service base eligibility / gate memory consolidation | （多為內部基礎建設 — 通常併入「內部優化」或不出現） |
| DisplayContext contract manifest guard | （純內部一致性防護 — 通常不必出現在 standup） |

The test: read the bullet aloud to someone who has never seen the code. If they can picture what changed for a user, it's ready. If they'd ask "what's a projection / a reader audit / Redis?", translate again. Keep the `NEX-XXXX` code as a tag at the end for anyone who wants to dig — but the words before it must stand on their own.

For a business-facing item in **昨天已完成**, prefer the fuller plain-outcome form that carries the *why/what-it-unlocks* clause (the Race Explorer row above is the model — `…接上新的賽事資料庫，為支援更多賽事打底`, not the bare `…接上新資料庫`). It's a touch more text, but for user/product work the extra context is what makes the line useful to the lead briefing onward. Don't extend this to internal plumbing or to the forward-looking sections.

## Step 4 — The forward-looking sections

- **🎯 今日重點 is a forward guess.** Seed it from In-Progress tickets + open PRs + memory's `Now`. It's a draft the user edits before posting — but do **not** print a draft-marker line; just emit the bullets. A blank plan is useless; an editable guess is useful. Apply the same business-language translation here, and the same dormant-epic filter from Step 2.
- **🙋 需要幫忙 defaults to「（無）」.** Only fill it from a real blocker or a PR genuinely waiting on someone. Never fabricate a help-request to look busy — an empty 需要幫忙 is the normal, honest case.

Note: git/Linear can't see non-engineering work (customer visits, sales, meetings). By default the skill does **not** emit a placeholder for it — if the user did off-git work that day, they add a line or two themselves.

## Step 5 — Deliver

Print the standup inline as one clean copy-paste block (fenced), so the user can lift it straight into the channel. Keep ticket references as bare `（NEX-A / NEX-B）` tags listing every ticket the bullet spans — short and quiet. Only when a day is genuinely bug-heavy and the team lead's "票號帶連結" rule kicks in, expand the roll-up's codes to full `https://linear.app/nexrex/issue/NEX-XXXX` URLs (Slack unfurls them).

Then stop. Don't append "要不要我也…" follow-up offers — the user will edit the draft and post it themselves.

## Skip rule

If the window has no NexRex-relevant git or Linear activity, don't pad it into a fake update. Say so plainly: `昨天沒有 NexRex 相關的 commit / ticket 進度 — 依團隊慣例今天可跳過。` The team lead explicitly blessed skipping empty days.

## Worked example (calibration target — real output, 2026-06-04)

A heavy ship day: 14 commits across nr-platform + nr-app, ~7 themes, plus dormant epics polluting Linear "In Progress". Compressed to three business-language bullets:

```
✅ 昨天已完成
- 賽事探索（Race Explorer）開始接上新的賽事資料庫，為支援更多國際賽事打底（NEX-1113 / NEX-832）
- 完成「學員↔教練」歸屬的資料切換收尾，聊天等功能會對應到正確的教練（NEX-1137 / NEX-1126）
- 多項使用者體驗修正與內部優化：月跑量排行榜數字更準（NEX-1146）、Garmin 活動不再顯示不完整（NEX-1145）、教練收件匣群組分流（NEX-1119）；另有顯示一致性與使用者標籤基礎（NEX-1128 / NEX-1105）＋數個小修

🙋 需要幫忙事項
-（無）

🎯 今日重點
- 繼續賽事資料平台：讓 Race Explorer 能呈現新資料庫的賽事（NEX-1113 / NEX-832）
- 修帳號設定頁「顯示名稱被截斷」的問題（NEX-961）
```

Notice the discipline: **no jargon** (no "Redis", "projection", "audit", "contract"); each bullet **lists every ticket its cluster spans** (`NEX-1113 / NEX-832`, `NEX-1137 / NEX-1126`) rather than one representative; purely-internal work folded into "內部優化" rather than each given a line; dormant epics (NEX-632/214/506) filtered out of 今日重點. Reproduce this altitude, not more.

## Common mistakes

| Mistake | Fix |
|---|---|
| **Engineer jargon in bullets** (Redis / projection / audit / SSOT / contract) | **Translate to the user/business outcome — Step 3. This is the #1 failure mode.** |
| Giving purely-internal plumbing its own line | At standup altitude, fold it into the roll-up ("內部優化") or drop it — only user/product-perceptible work earns a line |
| Tagging a bullet with only one ticket when its cluster spans several | List them all — `（NEX-A / NEX-B）`; never invent a code for a fix that has no ticket |
| Writing full sentences / a `dev-review`-style wall | Short plain-language outcomes; this is a 10-second skim, not a report |
| More than 3 bullets in a section | Cluster by ticket/theme, keep top 3, collapse the tail into the roll-up |
| Presenting 今日重點 as fact | Treat it as a forward guess from In-Progress tickets the user will edit — but don't print a draft-marker line |
| Surfacing dormant epics as today's focus | Filter against memory ownership — raw Linear "In Progress" has stale shells |
| Inventing a 需要幫忙 item | Default「（無）」unless there's a real blocker / PR waiting |
| Filtering git by `--author="Steven Wu"` | Use the email — the name-only filter misses `steven-wu-nexrex` commits |
| Padding an empty day | Honour the skip rule |
