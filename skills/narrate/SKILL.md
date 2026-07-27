---
name: narrate
description: "One-page visual brief of ONE topic at business altitude — what it is, where it stands, what's missing. Use when the user wants a topic made legible rather than decided: 「30 秒看懂」/「白話走一遍」/「這個 epic 在幹嘛」/「把架構帶我走一次」/ 圖解 / design review, about a ticket, epic, shipped system, pipeline, UI feature, or decision."
argument-hint: "[topic] [--full]"
---

# narrate

The **contract** is the product: same four blocks, same order, every run. The reader learns the
layout once, then navigates any brief in seconds. Business altitude throughout; code vocabulary is
confined to exactly one table column.

## The contract — the output IS this, in this order

| # | Block | Cap | Lives in |
|---|---|---|---|
| 1 | **BLUF** — 這是什麼、為誰、現在狀態 | ≤25 字，含一個狀態詞 | response text |
| 2 | **一張圖** — shape by topic type (next table) | ≤9 框；框上只有白話標籤（title ≤6 字 + 狀態副標 ≤4 字）；顏色 = 狀態或角色，附一行 legend | widget（無 widget 工具時 ASCII） |
| 3 | **關鍵節點表** — 節點｜白話職責｜位置 | ≤7 行；「位置」是全篇唯一放 code 詞彙的欄位 | response text（markdown 表） |
| 4 | **缺口** — 🔴🟡 + 去向（開票了／handoff／刻意延後） | ≤3 行；真的沒有就一行「無缺口」 | response text |

Then stop. If one next action is obvious, close with a single recommendation line — recommendation
or nothing.

Caps are ceilings, not quotas: 3 table rows and 1 gap line is a complete brief. When a shape wants a
tenth box, collapse the siblings into one box carrying a `×6` count and push the detail into the
node table or a `sendPrompt` drill-down.

Every identifier — class name, route, ticket ID, pipeline term — lives in block 3's 位置 column.
The diagram carries 白話 only; that separation is what keeps the brief readable at a glance.

**Complete when** all four blocks exist in order, every cap holds, no identifier appears on the
diagram, and block 4 states either real gaps or 「無缺口」.

## 圖形 by topic type

| Topic smells like | Draw | Grammar（細節在 references/visual.md） |
|---|---|---|
| UI/UX feature、頁面、入口 | **Sitemap** | container = surface（web／app），box = page，入口 gate 寫在 container 副標，顏色 = 狀態 |
| Pipeline／system／data flow | **泳道 blueprint** | 上泳道 = 使用者看到的，下泳道 = 系統節點，左→右資料流 |
| 設計／架構決策 | **Role-colored 架構圖** | 顏色 = 角色（SSOT／module／退役中），底部 amber banner = 終局 invariant |
| Bug 修復／incident | **Before / After** | 兩小格對照 |
| 純二選一決策 | **對照兩欄** | chosen vs rejected |
| Ticket 系列的派工順序 | — | 這不是 narrate；下一步做什麼交給 `/next-move` |

## Rendering

- Preferred: `mcp__visualize__show_widget`. Call `mcp__visualize__read_me({modules:["diagram"]})`
  once, silently. SVG mechanics, both colour grammars, and skeletons live in
  [references/visual.md](references/visual.md) — read it before the first render.
- Every box clickable — `onclick="sendPrompt('…')"` carrying a drill-down question. 一眼之後的第二眼
  要有地方去。
- Plain CLI with no widget tool: ASCII in the same grammar and caps, ≤30 lines × ≤80 cols.
- Blocks 1 / 3 / 4 always live in response text.

## Ground truth — before rendering

Lite by default, ≤5 reads total:

- ticket ID in scope → Linear state via MCP（top 3 張為限）；
- `git log --oneline -5 -- <path>` 或 grep ticket ID → 最近有沒有動；
- **每一個要進節點表的 path，grep 或 Read 驗證存在** — 那張表是這個 skill 的信用來源；
- Linear 說 Todo 但 code 已 shipped 這類矛盾，中性寫進缺口，不加戲。

Verification wanting more than 5 reads means you are in `--full` or in the wrong skill.

**Complete when** every path in the node table was verified this turn, and any contradiction found
is recorded in block 4.

## `--full`

Fires only on an explicit 「完整解析」/「每個環節都要 cover」/ onboarding 新人 / `--full`. The
one-pager still comes first — it is the cover page. Then walk depth in data-flow order:

- each layer opens with 「這層的任務是 X」, then 3–8 lines;
- a taxonomy inside a layer（6 analyzers／3 stages／4 tiers）goes in a table;
- an invariant inside a layer gets an inline `❗ 關鍵設計決策:` callout; a cross-layer rule is stated
  with its exception attached（「everything X **except** Y, because …」）;
- one sticky metaphor holds the whole system — concrete and mechanical（水管路、健檢報告）;
- verification escalates: every cited file:line checked; a ticket-cluster input gets an
  「輸入聲稱 vs 實際狀態」 table.

**Complete when** the one-pager preceded the walkthrough and every cited file:line was checked.

## Language & tone

zh-tw prose；技術詞保持英文（ticket ID、function 名、`idempotency`）；UX 文案引用保持原文。Dev lead
briefing a peer — 數字勝過形容詞（PR #822、2026-05-12、46 members）。缺口 block 是 dual-axis
honesty：shipped 歸 shipped、pending 歸 pending。
