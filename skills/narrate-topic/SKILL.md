---
name: narrate-topic
description: "Translate a Linear ticket, topic, epic, multi-ticket roadmap, OR a shipped pipeline / built system architecture into a business-first narrative with calibrated technical depth — anchored to verified ground truth (Linear + git + codebase + memory), structured as business problem → technical map → strategic logic → per-component translation → status verification → decision framework. Communicates in zh-tw with English technical terms. Two input shapes the skill handles: (A) ticket-cluster narration — multiple Linear tickets / a roadmap / an epic, items are tickets; (B) system narration — an already-shipped pipeline / engine / data-flow / built architecture, items are layers / engines / stages. Use whenever the user wants the big picture of work they didn't author or has half-forgotten: '/narrate-topic', '解析這串 ticket', '這個 epic 在幹嘛', '幫我看懂這個 roadmap', '把這份分析解析給我聽', '我對這系列實在沒概念', '為什麼要這樣排', '解析這份建議', '白話走一遍 [系統]', '搭配 pipeline 架構圖跟我分析', '把架構帶我走一次', '解釋這個 pipeline / engine / 系統', 'data flow 帶我走一遍', '每個環節都要 cover 到', or when handing a fresh person (PM, co-founder, new engineer) into a workstream. Strongly trigger when the user pastes a multi-ticket analysis OR asks for a built-system walkthrough and says 解析/解釋/翻譯/白話/帶我走 — even without naming the skill. CRITICAL difference from adjacent skills: this is read-only legibility, not strategy (strategic-next), restructuring (topic-to-tickets), or critique (reverse-thinking). Always verify cited state — ticket status OR cited file:line / function / invariant — against Linear + git + codebase before narrating; memory and quoted analyses lag merges."
status: active
tags: [core, communication, narrative, zh-tw]
---

# narrate-topic — Ticket / topic / epic → business-first narrative

You are translating a piece of work — one ticket, a cluster, an epic, someone else's roadmap, OR an already-shipped pipeline / built system architecture — into a story a busy human can read in 2 minutes and act on. The audience is usually the user themselves (revisiting work they delegated, saw cold, or shipped a few weeks ago and forgot the shape of), but it can also be a hand-off to a PM, co-founder, or a new engineer.

Two input shapes show up most often. Recognize which you're in — the spine adapts:

| Mode | Input looks like | "Item" in section 4 means | Sections 3 + 5 |
|---|---|---|---|
| **A. Ticket-cluster narration** | a roadmap, an epic, a list of Linear tickets, a multi-ticket analysis someone wrote | a ticket | full — strategic ordering matters, ticket states must be verified |
| **B. System narration** | a shipped pipeline, an engine, a data-flow architecture; user wants the whole built system explained layer-by-layer | a layer / engine / stage / sub-system | compressed — the system is already built (no future ordering decisions); status verification becomes invariant + file-path verification |

Recognize early which mode you're in. The verification you do, the diagram you draw, and the per-component shape all key off this.

The output is a self-contained briefing in zh-tw, with English technical terms (function names, file paths, ticket IDs, `webhook`, `ingestion`, `OAuth1`, `idempotency`, etc.) left in English. This matches how bilingual dev work reads naturally.

The skill is **read-only legibility**. It does not propose what to do next, restructure tickets, or challenge the plan — see the routing table below for when to hand off.

## When this triggers vs. adjacent skills

| If the user wants… | Use… |
|---|---|
| 看懂這個 initiative / epic / roadmap | **narrate-topic** (this, Mode A) |
| 白話走一遍已 ship 的 pipeline / engine / 系統架構 | **narrate-topic** (this, Mode B) |
| 想清楚下一步該做什麼 | `strategic-next` |
| 把一個 topic 拆 / 重組成 PR-shaped tickets | `topic-to-tickets` |
| Challenge / 逆向思考一個既定計畫 | `reverse-thinking` |
| 重建 project context（不限一個 initiative） | `catchup` |
| 同步 memory + Linear + git 到最新真相 | `latest` |

This skill *can* point out broken assumptions in the input (e.g. a ticket the input treats as upcoming is actually shipped). That's verification, not critique — flag it neutrally and move on. If the user then wants a structural rethink, hand off to `reverse-thinking`.

## The narrative spine (always in this order)

Every output follows these six sections. For a single small ticket, collapse to (1)(2)(4)(6). For a roadmap of 5+ items, use all six. For a **system narration** (Mode B), keep sections (1)(2)(4)(6) full and compress (3)(5) — the system is already shipped so strategic ordering has no future decisions to make, and status verification becomes invariant + file-path verification rather than ticket-state verification. Never reorder — the reader is being onboarded; structure does the work.

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

### 4. Per-component translation

For each component, **3–5 lines** (or one longer paragraph + a sub-system table when the component fans out into stages / analyzers / tiers). "Component" means:

| Mode | Component = |
|---|---|
| A. Ticket cluster | one Linear ticket |
| B. System narration | one layer / engine / stage in the data-flow diagram from section 2 |

Shape (same for both modes):

- **Business translation** — what does this mean for the user / ops / cost?
- **Architectural surface touched** *(required)* — which contract / state field / queue / invariant from section 2 does this modify, own, or read from? Name the *leverage point*, not just the file. E.g. "adds `last_webhook_at` write to the credential health surface" beats "modifies `user_service.py`". For Mode B, this is the layer's role in the data flow — what data shape comes in, what comes out, what side-effects happen here.
- **Why this order** — Mode A: what does the ticket unlock, what does it depend on (in terms of section 2 surfaces). Mode B: where does this layer sit in the data flow, what's upstream / downstream, what does it pass to the next layer.
- **Concrete anchor** — file:line, function name, PR number, or numeric fact so the reader can navigate code afterward
- **Sub-system decomposition** *(when applicable)* — if this component has internal taxonomy (3 stages, 6 analyzers, 4 tiers, N RPC kwargs, etc.), follow with a Pattern I table. Don't bury sub-systems as prose; the table IS the explanation.

Never copy the ticket description (or the file's docstring) verbatim. Synthesize. If the AC / code reads like an engineering checklist, your job is to surface the *architectural meaning* — what part of the system this touches and what invariant it preserves or restores. For Mode B, lead each component with a one-line "**這層的任務是 X**" framing before the deeper unpack — the reader needs to feel the layer's purpose in one sentence before they can absorb the detail.

**Mode B ordering**: follow the data flow (input → persistence → trigger → execution → read → frontend), not "biggest ticket first" or "highest confidence first". The reader is being walked through the system; data flow is the natural narrative arc.

### 5. Status verification table
**Mandatory** whenever the input claims any state ("this is next", "this is done", "this depends on…", "file X is at this path", "function Y does Z", "invariant W still holds"). Memory snapshots, quoted analyses, and architecture docs all lag merges; the cost of one extra `gh` / `git log` / `grep` call is far less than the cost of acting on a closed ticket or a renamed function.

**Mode A** (ticket cluster): verify ticket states + dependency claims.
**Mode B** (system narration): verify cited file:line, function names, layer names against current code — and verify the load-bearing invariants you plan to claim are still upheld by the current implementation (a doc-stated invariant doesn't automatically mean the code still enforces it).

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

Two scales — pick the one that fits the input.

**A.1 — Quick overview** (one line, 3–7 nodes). Mode A default. The architecture exists to *frame* where each ticket sits; you don't need to deeply explain every node.

```
Garmin 雲端 → webhook (Cloud Run) → Pub/Sub → ingestion consumer → Firestore → API → app
```

**A.2 — Numbered layered walkthrough** (5–8 numbered blocks with ASCII rules). Mode B default. Each numbered layer becomes one entry in section 4 — the diagram is the **table of contents** for the per-component walkthrough.

```
═══════════════════════════════════════════════════════════════════
  ① 資料源（Input）
═══════════════════════════════════════════════════════════════════
   Source A (webhook push)   Source B (API call)   Source C (user UI)

═══════════════════════════════════════════════════════════════════
  ② Persistence layer
═══════════════════════════════════════════════════════════════════
   sync_atomic ──▶ products / variants  +  watermark bump

═══════════════════════════════════════════════════════════════════
  ③ Trigger / orchestration layer
═══════════════════════════════════════════════════════════════════
   on user open ──▶ stale check ──▶ enqueue job

═══════════════════════════════════════════════════════════════════
  ④ Execution layer (engines, runners, drain)
═══════════════════════════════════════════════════════════════════
   ┌──── Engine X ────┐   ┌──── Engine Y ────┐
   │  L1 / L2 / L3    │   │  L1 / L2 / L3    │
   └──────────────────┘   └──────────────────┘

═══════════════════════════════════════════════════════════════════
  ⑤ Read / aggregator layer
═══════════════════════════════════════════════════════════════════
   ...

═══════════════════════════════════════════════════════════════════
  ⑥ Frontend
═══════════════════════════════════════════════════════════════════
   ...
```

Heavy `═══` rules separate top-level layers; light arrows / pipes inside a layer. Number every layer — section 4's per-component entries reference these numbers so the reader can flip between diagram and detail without losing place. When a layer has parallel sub-engines (PH vs SV), use ⑤-A / ⑤-B so the cross-engine relationship is visible at diagram level.

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

**Where to place invariants — two options, pick by context:**

- **Up-front list (section 2c)** — when the invariants are cross-cutting (e.g., "single writer per result table" spans both engines)
- **Inline at the layer they govern** — when the invariant is layer-specific. Use a `❗ 關鍵設計決策:` (or `❗ Key design decision:`) prefix so the reader's eye catches it while their working memory contains the layer:

  > L3 LLM **only references** L2's `field_suggestions[]` by index — never regenerates `suggested_value` / `acp_path`. Mismatch → L3 treated as fail → stub.
  >
  > ❗ 關鍵設計決策：信任邊界收斂。L3 做整體判斷（narrative + 排序），L2 已算完的具體欄位不該被 L3 蓋掉，否則會出現「L2 說改 GTIN 成 0123，L3 卻說改成 4567」的不一致。

Inline placement is more sticky because the invariant arrives next to the code path it constrains. Don't double-list — if you call it out inline, drop it from section 2c.

### Pattern G.1: Cross-cutting exception pointers

When an architectural rule has the shape "**everything goes here EXCEPT X**", name the exception explicitly. The rule alone is half the picture; the exception is what makes the rule load-bearing — readers who only see the rule get confused when they encounter the exception in code and assume the rule is broken.

Examples:

- "Webhook never triggers LLM inference. **The exception**: the PH→SV promotion event inside `persist_product_health_run` — but by the time PH writes a fresh row, the PH run itself was user-triggered, so the SV cascade it fires is still downstream of a user action."
- "Engines never `import` each other. **The exception**: the outbox event written through `analysis_jobs` — read-only path, no synchronous calls."
- "Repository methods never contain business logic. **The exception**: `_handle_supabase_result()` does data-shape unwrapping that's arguably 'business' — kept here because the alternative is leaking error-shape handling into every service caller."

Pattern: name the rule → say "**The exception**:" → name what + why the exception is admissible despite seeming to violate the rule.

### Pattern H: Failure-mode mapping
Use when multiple tickets address **different failure classes of the same system**. This is the highest-density pattern for engineering audiences — it makes the problem space's *shape* visible.

| Failure class | Symptom | Detect | Recover |
|---|---|---|---|
| Webhook lost in transit | activity never arrives | NEX-792 (`last_webhook_at` gap) | NEX-793 (summary backfill) |
| OAuth refresh failed | user silent, no error visible | NEX-792 (`last_auth_failure_at`) | separate fix |
| GPS payload malformed | route blank on map | NEX-829 (forensic) | NEX-829 (transformer fix) |
| Lap data incomplete | interval pace mismatch | NEX-516/517 (FIT file pull) | NEX-515 (precision fix) |

### Pattern I: Sub-system decomposition

When one component / layer / engine has internal taxonomy — 3 stages, 6 analyzers, 4-tier classification, N RPC parameters, multiple state-machine states — don't bury it as prose. Decompose into a labeled table inside that component's section 4 entry.

The principle: when a component's role is "**fan out to N sub-components**", the table IS the explanation. Without it, the reader has to keep `analyzer × 6` or `stage × 3` in their head as a vague count; with the table, they scan and absorb in one breath.

Example — explaining what a Quality stage of 6 analyzers does:

| Analyzer | What it judges | Cost |
|---|---|---|
| `content_quality` | title / description AI-readability + key attribute coverage | 1× LLM |
| `media_quality` | image coverage + alt text correctness | 1× LLM |
| `pricing_quality` | price structure incl. variant breakdown | 1× LLM |
| `variant_quality` | variant attribute consistency (size × color × material) | 1× LLM |
| `seller_trust_quality` | warranty / return_window / shipping policy signals | 1× LLM |
| `url_quality` | handle / canonical URL cleanliness | 1× LLM |

Pair this with Pattern A.2 — the numbered layer in the diagram says "Quality × 6 analyzers"; the section 4 entry shows what each one does. The diagram is the table of contents; this table is one of its expansions.

**Other shapes this pattern fits:**

- A 3-stage pipeline (L1 / L2 / L3) — table of stage × input × output × LLM-cost
- A 4-tier classification (`t1_one_click` / `t2_fix_in_admin` / `t3_guidance` / `t4_guidance_admin`) — table of tier × meaning × where it surfaces
- An RPC with 8 kwargs — table of arg × role × default
- A state machine with 5 statuses — table of status × meaning × allowed transitions

If you find yourself writing "and there are six analyzers, namely content_quality, media_quality, pricing_quality, ..." in prose, stop and decompose into a table instead.

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

- **Burying the lede.** If your first sentence is a ticket recap (Mode A) or a layer enumeration (Mode B), restart. The **business problem** comes first.
- **Trusting the input.** Always verify. Memory, quoted analyses, and architecture docs all lag merges.
- **Mode-blindness.** Defaulting to ticket-cluster spine when the input is a built system (or vice versa). Detect mode early — look at whether the user is asking "what should we build / why these tickets" (Mode A) or "explain how this thing works / walk me through it" (Mode B). The spine adapts.
- **Sub-system as prose.** If a layer has 6 analyzers / 3 stages / 4 tiers and you wrote "and there are six analyzers, including content quality, media quality, ..." in prose, that's a Pattern I table waiting to happen. Decompose.
- **Invariants only in a top list.** Cross-cutting invariants belong in section 2c, but layer-specific invariants land harder inline at the layer they govern with a `❗ 關鍵設計決策:` callout. Don't default-list everything at the top.
- **Rule without exception.** When the system has "everything X EXCEPT Y" architectural carve-outs (Pattern G.1), naming just the rule leaves the reader confused when they hit Y in code. Always name the exception alongside.
- **Over-engineering single tickets.** A standalone ticket doesn't need the full 6-step spine. Collapse to (1)(2)(4)(6).
- **Recommending instead of explaining.** Skill stops at presenting options. The user decides.
- **Code-review prose.** If the briefing reads like a PR diff, you've over-indexed on technical detail. Cut to one anchor per claim — but for Mode B, "one anchor per claim" includes the architectural surface, not just file:line.
- **No metaphor.** A briefing without at least one sticky image is forgettable. Add one even if it feels obvious. Mode B metaphors land best when they map the *whole system* to a real-world structure with parallel parts (健康檢查 + 求職市場 etc.).
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

## Worked example 2 (Mode B — system narration, compressed)

**Input**: User just shipped Task 7 of a webhook→LLM decoupling refactor and says "白話的方式搭配 pipeline 架構圖跟我分析，每個環節都要 cover 到，比方說 catalog API 打回來會經過 L1 L2 L3 的分析，這個地方都需要講解."

**Process** (different from Mode A — no Linear states to fetch; ground truth is the codebase):
1. Read the architecture SSOT (`docs/architecture/<topic>.md` or equivalent) for the layer naming
2. Trace data flow from input sources to frontend — name every layer the data passes through
3. Inventory sub-systems in each layer (engines × stages × analyzers × tiers) — these become Pattern I tables
4. Find load-bearing invariants in their natural layer (for inline `❗` callouts) + cross-cutting exception rules (Pattern G.1)
5. Verify cited file:line / function names against current code (Mode B's analog of ticket-status verification)

**Output spine** (~1200–1800 zh-tw words; system narrations run longer than roadmaps because the system has more inherent surface — that's expected, not bloat):

1. **Business problem** (1 line) — what the merchant / business actually wants, not the technical scope. e.g. "商家把商品上 Shopify 之後，AI Shopping 那邊能不能搜到、排第幾、商品資訊夠不夠完整是黑箱"
2. **Pattern A.2 numbered layered diagram** — 6–8 numbered ASCII blocks from input to frontend, separated by `═══` rules. Parallel engines as ⑤-A / ⑤-B
3. *(Section 3 compressed)* — system already shipped, no future ordering decisions. Replace with a one-line pointer like "M3 剛改動的是 ③ 觸發層 — 之前 webhook 直接觸發 LLM，現在改成 ③ 內的 lazy enqueue gate"
4. **Per-component × 6–8** — one entry per ① ② ③ ... layer. Each:
   - One-line "**這層的任務是 X**" lead
   - Deeper unpack (3–8 lines)
   - Pattern I sub-system table when the layer has internal taxonomy (e.g. ⑤-A PH 那層展開 6-analyzer 表 + 3-stage 表 + 4-tier 表)
   - Mid-narrative `❗ 關鍵設計決策:` callouts for invariants specific to this layer (e.g. "L3 不重新生 suggested_value")
5. *(Section 5 compressed)* — invariants + cited file:line already verified during process step 5. Surface anything stale inline ("doc says Pattern X here, code shows Pattern Y").
6. **Pattern G.1 cross-cutting exceptions** — explicitly name the "rule + exception" pairs that span layers (e.g. "Engines never import each other. **The exception**: PH→SV promotion event via outbox.")
7. **Pattern D sticky metaphor** — Mode B metaphors tend to land when they map the *whole system* to a real-world structure with similar parts. e.g. "整個系統像醫院健康檢查（PH）+ 求職市場分析（SV）雙報告，aggregator 是合報告的家醫。LLM 不被動觸發 — 商家走進診間才看片，掛號系統不會自動連續看片。"
8. **Decision close** — Mode B options skew toward "next deepening" rather than "which ticket first". e.g. "如果你想 deep-dive 某一層 → ... / 如果你想知道下一張要做什麼 → ... / 如果你想看某條 invariant 怎麼 enforce → ...". One concrete hand-off line ("要不要我 ultrathink ...") closes.

The layered structure is the load-bearing part. If a reader can navigate from the ① ② ③ ... diagram into any per-layer entry and back out without losing context, the narration is doing its job.

## Operating notes

- **Use extended thinking** for the synthesis step. Ground truth gathering is mechanical; synthesis is where think-time pays.
- **Spawn an Explore sub-agent** for multi-ticket inputs (3+) — they can gather Linear states + PR + git log in parallel without polluting your main context.
- **Don't paste full Linear descriptions** back to the user — synthesize them. The user already saw the original.
- **One-pass output**. Don't draft and revise visibly. Think, verify, then write the briefing in one clean pass.
