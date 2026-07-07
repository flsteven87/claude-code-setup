---
name: narrate
description: "One-page visual brief of ONE topic — a ticket, epic, shipped system, pipeline, UI feature, or decision. Replaces narrate-glance and narrate-topic (both old names route here). Use when the user wants to understand what something is or where it stands at business altitude: '/narrate', '30 秒看懂', 'tldr', '5 句話', '圖解', '白話走一遍', '跟我說明現況', '這個 epic 在幹嘛', '解析這串 ticket', '把架構帶我走一次', 'sitemap mental model', '視覺帶我看設計', 'design review', '架構圖講重點', or any 白話/解析/視覺化 request about one topic ('完整解析'/'每個環節都 cover' → same skill, --full). Read-only legibility — NOT strategy (strategic-next), ticket restructuring (topic-to-tickets), critique (reverse-thinking), dispatch ordering (dispatch-strategy), or whole-project rebuild (catchup)."
status: active
tags: [core, communication, narrative, zh-tw, glance]
---

# narrate — 一個主題 → 一頁固定格式 glance

## Overview

Format invariance is the product: same four blocks, same order, every time — the reader learns the layout once, then navigates any brief in seconds. Business altitude first; code vocabulary is confined to exactly one table.

Built from session-log mining (2026-07): the old pair failed by varying output shape per call (reader re-orients every time) and by letting code terms leak into diagrams while business framing leaked out. The fix is a contract, not more guidance.

## The contract — the output IS this, in this order

| # | Block | Hard cap | Lives in |
|---|---|---|---|
| 1 | **BLUF** — 這是什麼、為誰、現在狀態 | ≤25 字，含一個狀態詞 | response text |
| 2 | **一張圖** — shape by topic type (next table) | ≤9 框；框上只有白話標籤（title ≤6 字 + 狀態副標 ≤4 字）；顏色=狀態或角色，附一行 legend；code 識別字與 ticket ID 一律禁止上圖 | widget（無 widget 工具時 ASCII） |
| 3 | **關鍵節點表** — 節點｜白話職責｜位置 | ≤7 行；「位置」欄是全篇唯一允許 code 詞彙的地方（file path、flag、API、ticket ID）；每個 path 都先驗證 | response text（markdown 表） |
| 4 | **缺口** — 🔴🟡 + 去向（開票了／handoff／刻意延後） | ≤3 行；真的沒有就一行「無缺口」 | response text |

Then stop. No summary, no options menu, no 「希望這對你有幫助」. If one next action is obvious, close with a single recommendation line — recommendation or nothing (Response Shape rule).

Caps are ceilings, not quotas — 3 table rows and 1 gap line is a fine brief.

## 圖形 by topic type

| Topic smells like | Draw | Grammar（細節在 references/visual.md） |
|---|---|---|
| UI/UX feature、頁面、入口 | **Sitemap** | container = surface（web／app），box = page，入口 gate 寫在 container 副標，顏色 = 狀態 |
| Pipeline／system／data flow | **泳道 blueprint** | 上泳道 = 使用者看到的，下泳道 = 系統節點，左→右資料流 |
| 設計／架構決策 | **Role-colored 架構圖** | 顏色 = 角色（SSOT／module／退役中），底部 amber banner = 終局 invariant |
| Bug 修復／incident | **Before / After** | 兩小格對照 |
| 純二選一決策 | **對照兩欄** | chosen vs rejected |
| Ticket 系列的派工順序 | — | 這不是 narrate；交給 dispatch-strategy（wave 圖是它的） |

## Rendering

- Preferred: `mcp__visualize__show_widget`. First call `mcp__visualize__read_me({modules:["diagram"]})` once, silently. SVG mechanics + both color grammars + skeletons: read [references/visual.md](references/visual.md) before the first render.
- Every box clickable — `onclick="sendPrompt('…')"` with a drill-down question. 一眼之後的第二眼要有地方去。
- Fallback（plain CLI，無 widget 工具）: ASCII in the same grammar and caps, ≤30 lines × ≤80 cols.
- Blocks 1／3／4 always live in response text — never inside the widget.

## Ground truth（render 之前，不可省）

Lite by default — ≤5 reads total:

- Ticket ID in scope → Linear state via MCP（top 3 張為限）
- `git log --oneline -5 -- <path>` 或 grep ticket ID → 最近有沒有動
- **凡是要進節點表的 path，一律 grep／Read 驗證存在** — 那張表是這個 skill 的信用來源
- graphify shortcut: `<surface>/graphify-out/` 存在且 `.last_build_head` 新 → 節點與 path 直接取自 `GRAPH_REPORT.md`，不重讀 code
- 發現矛盾（Linear 說 Todo、code 已 shipped）→ 中性寫進缺口，不加戲

If verification wants more than 5 reads, you are either in --full or in the wrong skill.

## --full（opt-in，僅在使用者明說時）

Triggers: 「完整解析」／「每個環節都要 cover」／onboarding 新人／`--full`。One-pager 仍然先出 — 它是封面頁，永不跳過。之後才是深度走讀，依資料流順序：

- 每層開頭一句「這層的任務是 X」，再 3–8 行展開
- 層內有 taxonomy（6 analyzers／3 stages／4 tiers）→ 表格，禁止散文列舉
- 層內 invariant 用 `❗ 關鍵設計決策:` inline callout；跨層規則連例外一起講（「everything X **except** Y, because …」）
- 一個 sticky metaphor 收整個系統（具體、機械式 — 水管路、健檢報告；不要 "like a journey"）
- 驗證升級：cited file:line 全查；ticket-cluster 輸入附「輸入聲稱 vs 實際狀態」表

## Language & tone

- zh-tw prose；技術詞保持英文（ticket ID、function 名、`idempotency`）；UX 文案引用保持原文
- Dev lead briefing a peer — 數字勝過形容詞（PR #822、2026-05-12、46 members）
- 缺口 block 是 dual-axis honesty：shipped 歸 shipped、pending 歸 pending，不合併美化

## Anti-patterns（真實 baseline 失敗，勿重演）

| Mistake | Fix |
|---|---|
| Class 名／route／ticket ID／pipeline 術語出現在圖上 | 圖上白話；識別字進節點表「位置」欄（GREEN 測試實際漏過 ticket ID，勿重演） |
| 第 10 個框 | 同類收成一框 + 「×6」count；細節進表或 sendPrompt |
| Prose 重述圖的內容 | 圖載結構、字載 why — 重複的那句刪掉 |
| 以 2–3 個選項菜單收尾 | Recommendation or nothing |
| 沒驗證就把 path 寫進節點表 | 表裡每個 path 都 grep 過 |
| 因為尷尬而略過缺口 | 缺口是這個 skill 的存在理由之一 |
| 湊滿格 | 4 塊是上限不是配額，短就短 |
| 為了「完整」自動升級 --full | --full 只在使用者明說時 |
