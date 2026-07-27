---
name: reverse-thinking
description: "Audit a plan, spec, or roadmap against what the endgame actually requires, rather than against its own framing. Use before committing to build non-trivial pre-planned work, or when the user asks whether a plan is best practice, 「逆向思考」, 「戰略檢視」. Also reachable in `distill` mode to set the end-state north star before `/mattpocock-skills:grill-me`."
argument-hint: "[plan/spec path] [--distill]"
---

# Reverse Thinking — 從終局倒推檢視計畫

A plan is anchored on tasks, milestones, and increments. That framing makes it easy to execute a
clean plan that drifts from the **終局** — because the plan's own narrative hides what the endgame
needs but the plan never wrote down.

Reverse thinking flips the order: **蒸餾終局 → 倒推必要條件 → 對照 codebase 實況 → 這份計畫是在往那裡
走，還是在累積對它的債？**

Plan quality is measured as distance from the endgame. A perfectly executed plan pointed the wrong
way is more dangerous than a rough one pointed right.

## Mode

| Mode | 用途 | 輸入 | 產出 |
|---|---|---|---|
| `distill` | Pre-brainstorm 設 north star | 一個 topic 或對話 | **只有 Part A** |
| `audit`（預設） | Plan / spec 寫完後的戰略審計 | spec.md + plan.md + codebase | **Part A–F 全跑** |

`distill` has no codebase to compare against, so it stops after Part A and hands
`/mattpocock-skills:grill-me` a north star. A topic with no plan behind it belongs in `distill`;
everything else defaults to `audit`.

Reserve this skill for work whose shape is still negotiable — multi-milestone plans, hard-to-revert
architecture decisions, milestone orders driven by ease rather than value delivery, plans quoting a
現狀 that has not been re-checked in a while. A single-PR feature or a scoped linear task is already
past the point where reverse thinking pays.

---

## Part A — 蒸餾終局（ultrathink）

Read every user story and acceptance criterion, then compress the whole vision into:

1. **一句話** — the real user experience, not a feature list. 壓不進一句就是還沒蒸餾夠。
2. **一張架構圖** — the loop or flow that must exist in production. 畫不出來就是還沒想通。
3. **3–5 個 invariants** — 「為了讓這件事成立，X 必須永遠為真」.

This is the reference frame every later part judges against.

**Complete when** the sentence, the diagram, and the invariants all exist. `distill` ends here with
a handoff line to `/mattpocock-skills:grill-me`.

## Part B — 倒推必要條件

Work backwards from the endgame: what **must** be true for it to run? One row each:

| Precondition | 目前 codebase 狀態 | 計畫哪個 task 處理 | Gap? |
|---|---|---|---|

- ✅ 已滿足且計畫尊重現狀 → 不用動
- 🟡 部分滿足 → 該 task 是 plumbing 而非 invention（工作量被高估）
- 🔴 未滿足且計畫沒處理 → **gap**

**Complete when** every invariant from Part A has at least one precondition row, and every row
carries a verdict.

## Part C — Codebase 實況（ground truth）

The plan's description of the現狀 is a claim, not evidence. Every claim about the codebase gets a
`file:line` citation from a file you read this turn. Contradictions worth hunting:

- 「X 是 stub」→ 真的沒實作嗎？
- 「需要新增 Y」→ Y 是不是已經以另一個名字存在？
- 「資料在 path Z」→ 確認確切的 key/field 路徑
- 「工具／endpoint W 不存在」→ 搜索過再下結論

Explore subagent 跑廣度、Read 跑關鍵檔案深度，平行進行。

List every inconsistency between plan assumption and codebase reality, ranked:

- 🔴 **Load-bearing** — 會造成 silent failure、test 失效、或白工
- 🟡 **Scope-shifting** — 顯著改變工作量或風險
- 🟢 **Cosmetic** — 描述錯但方向對

**Complete when** every load-bearing claim in the plan has been checked against a file read this
turn, and each contradiction carries a `file:line`.

## Part D — Best-practice 維度

| 維度 | 問題 |
|---|---|
| 產品願景清晰度 | 能不能蒸餾成一句話？ |
| 架構一致性 | 每個 task 都推向終局，還是在累積要被刪掉的基礎設施？ |
| 現實對齊 | 計畫的假設符合 codebase 嗎？ |
| Milestone 排序 | 第一個 milestone 能不能產生 validation signal？ |
| 量測策略 | 我們要怎麼知道它有效？ |
| 風險識別 | 計畫有沒有指出可能出錯的地方？ |
| 可回滾性 | 每個 milestone 能獨立 revert 嗎？ |
| Scope gating | 存取／資格規則是宣告式還是散落的 patch？ |

An absent dimension is a gap, not a nit.

**Complete when** all eight dimensions have a verdict.

## Part E — Gaps 與重構建議

**Gap 是「缺什麼」，不是「錯什麼」** — 計畫沒有但終局需要的東西。常見類型：沒有 rollback 機制
（尤其 prompt 改動）、沒有 cost／latency 預算、沒有 observability 埋點、沒有 cold-start／資料稀疏
處理、沒有 Milestone 0 安頓前提條件、沒有 retire legacy 的 exit milestone。

建議永遠是這五段：

- **Keep** — 直接交付終局的 task
- **Reorder** — 把帶 validation signal 的工作拉前
- **Insert** — 把缺席的前提條件開成明確的 M0
- **Reduce** — 正在強化「終局要刪掉的元件」的 task
- **Delete / Defer** — 踩到已知 bug class 或產生 sunk cost 的 task

計畫的骨架通常是好的；修的是排序、假設、與缺失。

**Complete when** every 🔴 from Part C and every absent dimension from Part D appears in one of the
five buckets.

## Part F — RISK verdict

Downstream（Codex adversarial review、`/ship`）會讀這段，所以格式固定：一行 `RISK: LOW|MEDIUM|HIGH`
＋ 一行 rationale ＋ 最多一個觸發升級的關鍵 gap。

| Verdict | 條件 |
|---|---|
| `LOW` | Part C 無 🔴 + Part D 無缺席維度 + scope ≤ 5 files + 不動 schema／auth／dep／public API |
| `MEDIUM` | 有 🟡 scope-shifting 矛盾，或 1 個維度缺席但可補 |
| `HIGH` | 有 🔴 load-bearing 矛盾，或架構假設與 codebase 相悖，或多個維度缺席 |

**Complete when** the verdict line, the rationale, and the escalating gap (or its absence) are all
present.

---

以 2–3 個具體「下一步選項」收尾，讓使用者選。這是這個 skill 唯一該給選單的地方 —— 方向是使用者
自己的。
