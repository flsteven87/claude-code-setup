---
name: narrate-topic
description: "Translate a Linear ticket, topic, epic, or multi-ticket roadmap into a business-first narrative with calibrated technical depth — anchored to verified ground truth (Linear + git + codebase + memory), structured as business problem → technical map → strategic logic → per-item translation → status verification → decision framework. Communicates in zh-tw with English technical terms. Use whenever the user wants the big picture of an initiative they didn't author or has half-forgotten: '/narrate-topic', '解析這串 ticket', '這個 epic 在幹嘛', '幫我看懂這個 roadmap', '把這份分析解析給我聽', '我對這系列實在沒概念', '為什麼要這樣排', '解析這份建議', or when handing a fresh person (PM, co-founder, new engineer) into a workstream. Strongly trigger when the user pastes a multi-ticket analysis and says 解析/解釋/翻譯 — even without naming the skill. CRITICAL difference from adjacent skills: this is read-only legibility, not strategy (strategic-next), restructuring (topic-to-tickets), or critique (reverse-thinking). Always verify ticket states against current Linear + git before narrating — memory and quoted analyses lag merges."
status: active
tags: [core, communication, narrative, zh-tw]
---

# narrate-topic — Ticket / topic / epic → business-first narrative

You are translating a piece of work — one ticket, a cluster, an epic, or someone else's roadmap — into a story a busy human can read in 2 minutes and act on. The audience is usually the user themselves (revisiting work they delegated or saw cold), but it can also be a hand-off to a PM, co-founder, or a new engineer.

The output is a self-contained briefing in zh-tw, with English technical terms (function names, file paths, ticket IDs, `webhook`, `ingestion`, `OAuth1`, `idempotency`, etc.) left in English. This matches how bilingual dev work reads naturally.

The skill is **read-only legibility**. It does not propose what to do next, restructure tickets, or challenge the plan — see the routing table below for when to hand off.

## When this triggers vs. adjacent skills

| If the user wants… | Use… |
|---|---|
| 看懂這個 initiative / epic / roadmap | **narrate-topic** (this) |
| 想清楚下一步該做什麼 | `strategic-next` |
| 把一個 topic 拆 / 重組成 PR-shaped tickets | `topic-to-tickets` |
| Challenge / 逆向思考一個既定計畫 | `reverse-thinking` |
| 重建 project context（不限一個 initiative） | `catchup` |
| 同步 memory + Linear + git 到最新真相 | `latest` |

This skill *can* point out broken assumptions in the input (e.g. a ticket the input treats as upcoming is actually shipped). That's verification, not critique — flag it neutrally and move on. If the user then wants a structural rethink, hand off to `reverse-thinking`.

## The narrative spine (always in this order)

Every output follows these six sections. For a single small ticket, collapse to (1)(2)(4)(6). For a roadmap of 5+ items, use all six. Never reorder — the reader is being onboarded; structure does the work.

### 1. One-sentence business problem
Lead with what the **user or business is feeling**, not the technical scope. Open with the conclusion in one sentence; do not warm up.

Compare:
- ❌ "This is a critical initiative to improve our Garmin ingestion observability and webhook reliability." (technical scope, no pain)
- ✅ "Garmin 用戶常常跑完一場、App 上卻沒出現，而我們現在沒能力快速判斷漏在哪、也沒工具補回來。" (felt pain, then implied cost)

### 2. Technical architecture map

This is the load-bearing section. The reader needs to see the **system the work lives in** before they can navigate any individual ticket. Three sub-components go here — present in this order:

**(a) Control flow / pipeline** — 3–7 nodes, ASCII or short prose. Pick the spine; leave side branches out unless one is the actual bottleneck.

```
Garmin 雲端 → webhook (Cloud Run) → Pub/Sub → ingestion consumer → Firestore → API → app
```

**(b) Load-bearing surfaces** — name the interfaces / contracts / state stores / queues that hold the system together. Surface a table when there are 3+. This is what makes a narration "architectural" rather than "story-shaped":

| Surface | Role | Touched by |
|---|---|---|
| `BackfillService.queue_backfill_job()` | unified entry into async backfill pipeline | NEX-849, NEX-793 |
| `user_credentials.last_*_at` fields | sync health observable state | NEX-792 |
| webhook idempotency key | dedup guard against retry-storms | NEX-793 |

**(c) Invariants the architecture relies on** — 1–3 things that MUST hold for the system to work. These usually map 1:1 to the bug classes the work prevents.

- `last_sync_at` only advances on successful ingestion (else "looks healthy but isn't")
- Backfill job dedup keyed on `(user_id, time_window)` (else recovery webhooks get murdered)
- `HTTP 202` from Garmin ≠ data delivered; truth comes from the follow-up webhook

Naming the architecture this way pays for itself in section 3, because the strategic logic can then reference *which* surface or invariant each phase touches — and in section 4, each ticket can be located on the map instead of floating.

### 3. Strategic logic of the ordering
If multiple items are involved, explain the **grouping and ordering in business terms** — not "A blocks B" but "we build the road before we drive on it". This is the single most under-appreciated step. Lists without dependency reasoning feel arbitrary and forgettable.

Common shapes worth naming when they apply:
- **Capability → use case** — build the ability, then exercise it
- **Instrument → debug** — observability first, then root-cause anything
- **Forensic → fix** — understand before changing the code
- **Contract → implementation** — align the schema, then ship behind it
- **Migration → cleanup** — move first, delete after a release window

A phase table works well here:

| 階段 | 目的 | 對應票 |
|---|---|---|
| 1. 打通管線 | App 跟 backend 講同一種語言 | NEX-849 |
| 2. 裝儀表板 | 每個用戶 Garmin 健康度可見 | NEX-792 |

### 4. Per-item translation
For each ticket, **3–5 lines** in this shape:

- **Business translation** — what does this mean for the user / ops / cost?
- **Architectural surface touched** *(required)* — which contract / state field / queue / invariant from section 2 does this modify? Name the *leverage point*, not just the file. E.g. "adds `last_webhook_at` write to the credential health surface" beats "modifies `user_service.py`".
- **Why this order** — what does it unlock, or what does it depend on (in terms of the surfaces in section 2)?
- **Concrete anchor** — file:line, function name, PR number, or numeric fact so the reader can navigate code afterward

Never copy the ticket description verbatim. Synthesize. If the AC reads like an engineering checklist, your job is to surface the *architectural meaning* — what part of the system this touches and what invariant it preserves or restores.

### 5. Status verification table
**Mandatory** whenever the input claims any state ("this is next", "this is done", "this depends on…"). Memory snapshots and quoted analyses lag merges; the cost of one extra `gh` / `git log` call is far less than the cost of acting on a closed ticket.

| Ticket | 輸入聲稱 | 實際狀態 | 行動 |
|---|---|---|---|
| NEX-849 | 先做 | ✅ Done 2026-05-12 (PR #241) | 跳過 |
| NEX-792 | 第二張 | Backlog | 下一張 |

If anything in the input is structurally outdated (e.g. dependency target shipped, file path renamed, ticket cancelled), call it out in plain language: "這份分析寫的時候 NEX-849 還沒進 main，所以排在第一張；現在這張已經 ship，roadmap 的有效起點是 NEX-792。"

### 6. Decision framework
End with **2–3 decision-shaped options**, not a recommendation. Frame them as "if X then Y" so the user picks based on their own priorities. Offer one immediate hand-off ("要不要我 …" / "要不要我幫你 ultrathink …") as the closing line.

- 如果你想最短路徑解客訴 → 先動 NEX-781（已 In Review，可能只差驗證）
- 如果你想建長期能力 → 推 NEX-792（觀測層，後面整串都靠它）
- 如果你想先確認資料源乾淨 → 並行 NEX-516/517 In Testing 進度

Do NOT end with a summary or a "希望這對你有幫助". Briefing-style — the table of options IS the close.

## Ground truth verification (do this BEFORE writing the narrative)

The user's memory, Linear states, and pasted analyses all lag merges. Treat any input as a hypothesis until verified. **This step is non-negotiable** — it's where this skill earns its keep.

Run these in parallel (spawn an Explore sub-agent for multi-ticket inputs, inline for a single ticket):

| Source | What to check | Command |
|---|---|---|
| Linear | Current state + AC + recent comments | `mcp__linear__get_issue` for each cited ID |
| GitHub | Open / merged PRs linked to ticket | `gh pr list --state all --search "NEX-XXX"` |
| Git history | Squash commits referencing the ticket | `git log --all --oneline --grep="NEX-XXX"` |
| Codebase | Cited file paths / function names still exist? | `Grep` / `Read` (file path), `Grep` (symbol) |
| Memory | Any locked decisions, scope guardrails, or known bugs that change framing? | Read MEMORY.md + relevant `project_*.md` |

**Red flags that demand stop-and-verify before continuing:**
- Input claims a ticket is "next to do" — was it already shipped? (Garmin roadmap had NEX-849 as #1, but it merged the same day the roadmap was written.)
- Input cites a file path or function — does it still exist? Has it been renamed or moved?
- Input cites a dependency on another ticket — is that dependency still real, or did it get rescoped?
- Input claims a ticket is owned by person X — does Linear agree, or has it been delegated since?

For multi-ticket inputs, verify the **top 3–5 most load-bearing tickets first**, then expand only if something feels off. You don't need to verify every single line — verify enough to anchor the narrative.

**While verifying, also map the architectural surfaces.** Don't stop at "file exists / function exists". Note *which contracts, state fields, queues, or idempotency keys the tickets touch* — this is the raw material for section 2(b) and the per-item "architectural surface touched" field. A grep that returns 3 hits in a `BackfillService` class is more architecturally interesting than 30 hits in route handlers; weight accordingly.

## Calibration: how much technical depth?

**Default is technical-by-default, not light-by-default.** This skill briefs engineers — assume the reader will navigate code afterward, and pre-load the anchors they need.

Per major claim, include at least one of:
- The **architectural surface** being touched (contract, queue, state field, invariant) — preferred
- A file path + function name (e.g. `strava.py:2587-2693`)
- A numeric fact (ms, MB, count, rate, SLO target)
- A PR / commit SHA / ticket ID

Lean even heavier technical when:
- The dependency reasoning doesn't hold without it ("queue contract first — without unified `BackfillService.queue_backfill_job()`, every downstream job has a different shape")
- A metaphor would mislead without correction ("`HTTP 202 Accepted` is 'request received', not 'data delivered' — actual data arrives via follow-up async webhook")
- An invariant is non-obvious ("`last_sync_at` advances only on successful ingestion — that's why this field is the right observability target, not webhook receipt")
- The architecture has a non-trivial state machine, idempotency strategy, retry policy, or consistency model
- The user explicitly asks for more technical depth

Lean lighter **only** when:
- The audience is explicitly non-technical (PM hand-off — and even then, name the architectural surface in plain language)
- The strategic question is the gate, not the implementation
- Technical detail would obscure rather than illuminate

When in doubt: **add the sentence that names a contract, invariant, or state machine transition**. Cut the sentence that just shows you read the code without naming any leverage point.

## Writing patterns

### Pattern A: Pipeline map (ASCII)
Use when the work spans a multi-stage data or request flow.

```
Garmin 雲端 → webhook 推給我們 → 我們 ingestion → app 顯示
```

### Pattern B: Phase table
Use when the work has a clear before/during/after rhythm.

| 階段 | 目的 | 對應票 |
|---|---|---|
| 打通管線 | App 跟 backend 講同一種語言 | NEX-849 |
| 裝儀表板 | 每個用戶 Garmin 健康度可見 | NEX-792 |

### Pattern C: Status verification table
Use whenever input claims any ticket state. Never skip.

| Ticket | 輸入聲稱 | 實際狀態 | 行動 |
|---|---|---|---|
| NEX-849 | 先做 | Done 2026-05-12 | 跳過 |

### Pattern D: Sticky metaphor
Always include **at least one**. Readers retain metaphors longer than tables. Good metaphors are concrete, mechanical, and visualizable.

Examples that landed:
- 「資料管線像輸水管路。先確認進水口跟出水口接得起來，再每個閥門裝壓力錶，再準備備援水塔。」
- 「Observability ticket 是裝感應器，不是修水管。」
- 「`HTTP 202 Accepted` 是『我收到請求了』，不是『資料給你了』。」

Bad metaphors are abstract ("like a journey") or technical-pretending-to-be-metaphor ("like a pipeline" — that's just the literal thing).

### Pattern E: Decision framework (closing)
End with 2–3 "if X then Y" options. Offer one concrete hand-off line.

- 如果你想最短路徑解客訴 → 推 NEX-781（Tony 已 In Review）
- 如果你想建長期能力 → 推 NEX-792
- 如果你只想知道哪張現在最便宜可做 → 我幫你 ultrathink NEX-792 起手

### Pattern F: Load-bearing surfaces table
Use to name the interfaces / contracts / state stores / queues that hold the system together. **Strongly recommended** for any output covering 3+ tickets — this is what lets the reader see the architecture, not just the work-list.

| Surface | Role | Touched by |
|---|---|---|
| `BackfillService.queue_backfill_job()` | unified backfill entry point | NEX-849, NEX-793 |
| `user_credentials.last_webhook_at` | webhook health observable | NEX-792 |
| Pub/Sub `garmin-backfill-jobs` topic | async dispatch + retry boundary | NEX-849, NEX-793, NEX-850 |

### Pattern G: Invariants
Name 1–3 things that MUST hold. These often map 1:1 to the bug classes the work prevents — naming them gives the reader the "why this code path matters" frame.

- `last_sync_at` only advances on successful ingestion (else healthy-looking but stale)
- Backfill dedup keyed on `(user_id, time_window)` (else recovery webhooks get murdered by dedup)
- `HTTP 202` from upstream ≠ data delivered; only the follow-up webhook is ground truth
- Idempotency key on consumer side, not producer side (producer retries are cheap; double-writes are not)

### Pattern H: Failure-mode mapping
Use when multiple tickets address **different failure classes of the same system**. This is the highest-density pattern for engineering audiences — it makes the problem space's *shape* visible.

| Failure class | Symptom | Detect | Recover |
|---|---|---|---|
| Webhook lost in transit | activity never arrives | NEX-792 (`last_webhook_at` gap) | NEX-793 (summary backfill) |
| OAuth refresh failed | user silent, no error visible | NEX-792 (`last_auth_failure_at`) | separate fix |
| GPS payload malformed | route blank on map | NEX-829 (forensic) | NEX-829 (transformer fix) |
| Lap data incomplete | interval pace mismatch | NEX-516/517 (FIT file pull) | NEX-515 (precision fix) |

## Language & tone

- **Prose in zh-tw**, technical terms in English (ticket IDs, function names, file paths, English jargon `webhook`, `ingestion`, `idempotency`, `OAuth1`, `HTTP 202`).
- **Tone: dev lead briefing a peer**, not consultant pitching. Confident, direct, no hedging filler.
- **No filler phrases**: avoid "希望這對你有幫助", "綜上所述", "總的來說", "這是一個關鍵的", "to summarize".
- **No emoji** unless the user uses them first.
- **Cite specifics**: commit SHAs, PR numbers, file:line refs, ticket IDs — they're free credibility.
- **Numbers over adjectives**: "merged 2026-05-12, PR #241" beats "recently shipped".

## Memory connection

When relevant, cite cross-session lessons or locked decisions from `MEMORY.md` that change framing. Examples worth name-checking:
- A locked decision that explains why an obvious-looking alternative isn't on the table
- A G1–G4 invariant that constrains the design space
- A past lesson (e.g. "同一個表面症狀可能對應兩個不同的 invariant") that explains why the work was split this way

Cite the lesson by content, not by file. The reader doesn't need the filename to feel grounded.

## What this skill is NOT

- **Not strategic-next.** This explains existing work; it doesn't propose what to do next. The decision framework at the end is *option presentation*, not recommendation.
- **Not topic-to-tickets.** This is read-only — no Linear writes, no ticket restructuring, no Codex consultation.
- **Not catchup.** Catchup is broad project state. This is depth on one initiative.
- **Not reverse-thinking.** This skill takes the plan at face value (after verifying state). If you find yourself wanting to challenge the plan, stop and hand off.

If, after verifying ground truth, you discover the *whole framing* of the input is wrong (not just stale states — wrong premise), say so once and recommend handing off to `reverse-thinking`. Don't quietly rewrite the user's plan inside a narration.

## Failure modes (and how to recover)

- **Burying the lede.** If your first sentence is a ticket recap, restart. The business problem comes first.
- **Trusting the input.** Always verify. Memory and quoted analyses lag merges.
- **Over-engineering single tickets.** A standalone ticket doesn't need the full 6-step spine. Collapse to (1)(2)(4)(6).
- **Recommending instead of explaining.** Skill stops at presenting options. The user decides.
- **Code-review prose.** If the briefing reads like a PR diff, you've over-indexed on technical detail. Cut to one anchor per claim.
- **No metaphor.** A briefing without at least one sticky image is forgettable. Add one even if it feels obvious.
- **Filler close.** Decision-shaped options IS the close. No summary, no farewell.

## Worked example (compressed)

**Input**: User pastes a 9-ticket Garmin roadmap, says "我對這一系列在幹嘛實在沒概念，多帶一點技術".

**Process** (parallel where possible):
1. `mcp__linear__get_issue` × top 5 tickets → confirm states
2. `gh pr list --search "NEX-849"` → catch the recent merge
3. `git log --grep="NEX-849"` → confirm SHA + date
4. Grep cited file paths → confirm names current
5. Read relevant `project_*.md` memory if Garmin context exists

**Output spine**:
1. Business problem: "Garmin 用戶資料常常無聲消失，我們沒能力定因或補救" (1 line)
2. Architecture map:
   - Control flow: `Garmin 雲端 → webhook (Cloud Run) → Pub/Sub → ingestion consumer → Firestore → API → app`
   - Load-bearing surfaces table (3 rows: `BackfillService.queue_backfill_job()`, `user_credentials.last_*_at`, Pub/Sub topic)
   - Invariants list (3 items: `last_sync_at` advances on success only; backfill dedup keyed on `(user_id, time_window)`; `HTTP 202` ≠ delivered)
3. Strategic logic: 4-row phase table + 「先打通 contract、再裝感應器、再開補資料路、再驗證」paragraph that explicitly references which surface each phase touches
4. Per-item × 9 (collapsed into groups where natural): each 3–5 lines including the **architectural surface touched** (e.g. NEX-792 → `user_credentials.last_*_at` fields; NEX-793 → consumer-side idempotency + Garmin `/backfill/activities` call)
5. Status verification table: flag NEX-849 = Done (PR #241, merged 2026-05-12)
6. Failure-mode mapping table (Pattern H) showing which ticket detects vs recovers each failure class
7. Decision framework: 3 "if X then Y" options + one hand-off line

Total output: ~700–1000 zh-tw words. Mix of prose, ASCII pipeline, 4 tables (phase / surfaces / status / failure-modes), 1 metaphor (水管路).

## Operating notes

- **Use extended thinking** for the synthesis step. Ground truth gathering is mechanical; synthesis is where think-time pays.
- **Spawn an Explore sub-agent** for multi-ticket inputs (3+) — they can gather Linear states + PR + git log in parallel without polluting your main context.
- **Don't paste full Linear descriptions** back to the user — synthesize them. The user already saw the original.
- **One-pass output**. Don't draft and revise visibly. Think, verify, then write the briefing in one clean pass.
