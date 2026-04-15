---
name: reverse-thinking
description: "Use when reviewing an implementation plan, architecture spec, multi-milestone roadmap, or design doc before committing to build. Also usable in `distill` mode to set end-state north star before brainstorming. Triggers on 'is this plan best practice?', 'should we do it this way?', 'review my plan', 'ultrathink the plan', '逆向思考', '戰略檢視', or before starting any non-trivial pre-planned feature work."
---

# Reverse Thinking — 從終局倒推檢視計畫

**Don't evaluate a plan by its own framing. Evaluate it by what the end-state actually requires.**

---

## Mode（呼叫方必須指定）

| Mode | 用途 | 輸入 | 輸出範圍 | Token 量級 |
|---|---|---|---|---|
| `distill` | Pre-brainstorm 設 north star | 用戶的 topic / 對話 | 只跑 **Part A**（1 句 vision + 架構圖 + invariants） | 輕量 |
| `audit`（預設） | Plan / spec 寫完後的戰略審計 | spec.md + plan.md + codebase | **Part A–F 全跑**（F = RISK verdict，必備） | 重量 |

**關鍵原則：**
- `distill` 模式**不碰 codebase**（沒東西可對照），跳過 Phase 3–5
- `audit` 模式**必須輸出 Part F RISK verdict**，呼叫方（例如 `/building`）會讀
- 呼叫方沒指定 mode → 預設 `audit`。Topic 只是一句話而沒有 plan 時 → 應該用 `distill`

計畫是以「任務、milestone、增量」為錨。這讓你很容易執行一份乾淨俐落、但方向偏離終局的計畫 — 因為計畫的敘事本身會遮蔽「終局真正需要但沒寫進來」的東西。

逆向思考把評估順序翻轉：**先蒸餾終局 → 倒推必要條件 → 對照 codebase 實況 → 再問「這份計畫是不是在往那裡走，還是在累積對它的債？」**

---

## 何時用

- 開始一份多 milestone 實作計畫之前
- 用戶問「這計畫是不是 best practice？」、「該這樣做嗎？」、「幫我 ultrathink 一下」
- 計畫引用的現狀敘述很久沒更新（ticket description、舊 architecture 假設）
- Milestone 是依「好做」而非「價值交付」排序
- 架構決策難以 revert 時

**不適用**：小 bug fix、單一 PR feature、scope 明確的線性任務。

---

## Phase 1 — 蒸餾終局（Ultrathink）

讀完所有 user stories / acceptance criteria，把整個願景壓縮成：

1. **一句話** — 真實的用戶體驗（不是 feature 清單）。壓不進一句就是還沒蒸餾夠。
2. **一張架構圖** — production 裡必須存在的 loop/flow。畫不出來就是還沒想通。
3. **3-5 個 invariants** — 「為了讓這件事成立，X 必須永遠為真」的條件。

這階段的產物是後面所有判斷的 reference frame。

---

## Phase 2 — 倒推必要條件

從終局往回推：為了讓它能運作，什麼**必須**先為真？每一條開一行表格：

| Precondition | 目前 codebase 狀態 | 計畫哪個 task 處理 | Gap? |
|---|---|---|---|

- ✅ 已滿足且計畫尊重現狀 → 不用動
- 🟡 部分滿足 → 計畫該 task 是 plumbing 而非 invention（工作量被高估）
- 🔴 未滿足且計畫沒處理 → **這就是 gap**

Gap 是本次檢視最有價值的輸出。

---

## Phase 3 — 對照 codebase 實況（Ground Truth）

**絕對不相信計畫對現狀的描述。** 讀實際的檔案，每個關於 codebase 的宣稱都要 cite `file:line`。常見要 hunt 的矛盾：

- 「X 是 stub」→ 真的沒實作嗎？
- 「需要新增 Y」→ Y 是不是已經以另一個名字存在？
- 「資料在 path Z」→ 確認確切的 key/field 路徑
- 「工具/endpoint W 不存在」→ 搜索過再下結論

**策略**：Explore subagent 跑廣度 + Read 跑關鍵檔案深度，平行進行。

---

## Phase 4 — 找矛盾（Contradictions）

列出每一個「計畫的假設 vs codebase 現實」的不一致。按嚴重度排：

- 🔴 **Load-bearing**：會造成 silent failure、test 失效、或白工
- 🟡 **Scope-shifting**：顯著改變工作量或風險
- 🟢 **Cosmetic**：描述錯但方向對

每一條都要附 `file:line`。

---

## Phase 5 — 以 best practice 維度打分

不問「這份計畫寫得好不好」，問這些：

| 維度 | 問題 |
|---|---|
| 產品願景清晰度 | 能不能蒸餾成一句話？ |
| 架構一致性 | 每個 task 都推向終局，還是在累積要被刪掉的基礎設施？ |
| 現實對齊 | 計畫的假設符合 codebase 嗎？ |
| Milestone 排序 | 第一個 milestone 能不能產生 validation signal？ |
| 量測策略 | 我們要怎麼知道它有效？ |
| 風險識別 | 計畫有沒有指出可能出錯的地方？ |
| 可回滾性 | 每個 milestone 能獨立 revert 嗎？ |
| Scope gating | 存取/資格規則是宣告式還是散落的 patch？ |

**任何維度缺席都是 gap，不是 nit。**

---

## Phase 6 — 辨識缺失 + 重構建議

**Gap 是「缺什麼」，不是「錯什麼」。** 列出計畫**沒有**但終局需要的事物。常見類型：

- 沒有 eval harness / 量測系統
- 沒有 rollback 機制（尤其 prompt 改動）
- 沒有 cost / latency 預算
- 沒有 observability 埋點
- 沒有 cold-start / 資料稀疏處理
- 沒有 Milestone 0 來安頓前提條件
- 沒有 retire legacy 的 exit milestone

建議結構永遠是這五段：

- **Keep** — 直接交付終局的 task
- **Reorder** — 把帶 validation signal 的工作拉前
- **Insert** — 把缺席的前提條件開成明確的 M0
- **Reduce** — 正在強化「終局要刪掉的元件」的 task
- **Delete / Defer** — 踩到已知 bug class 或產生 sunk cost 的 task

**永遠不要建議「全部重寫」。** 已寫好的計畫通常骨架是好的，問題出在排序、假設、與缺失。

---

## 輸出格式

### `distill` 模式 — 只產 Part A

**Part A — End-state Ultrathink**：1 句 vision + 架構圖 + 3–5 invariants。

結尾給 brainstorming 一個 handoff：「north star 已設定，可以進 clarify 階段」。**不碰 Part B–F。**

### `audit` 模式 — Part A–F 全跑

1. **Part A — End-state Ultrathink**：蒸餾願景 + 架構圖 + invariants
2. **Part B — Reverse Thinking**：倒推 preconditions 表格
3. **Part C — Codebase Reality Check**：矛盾清單，全 cite file:line
4. **Part D — Best-Practice Critique**：維度評分 + gaps
5. **Part E — Restructuring Recommendation**：Keep / Reorder / Insert / Reduce / Delete
6. **Part F — RISK Verdict**（必備，供上游 pipeline 消費）：
   - `RISK: LOW` / `RISK: MEDIUM` / `RISK: HIGH`
   - 一行 rationale
   - 觸發升級的最關鍵 gap（最多 1 個）

**RISK 判定準則：**
- `LOW`：Part C 無 🔴 矛盾 + Part D 無缺席維度 + scope ≤ 5 files + 不動 schema/auth/dep/public API
- `MEDIUM`：有 🟡 scope-shifting 矛盾，或有 1 個維度缺席但可補
- `HIGH`：有 🔴 load-bearing 矛盾，或架構假設與 codebase 相悖，或缺多個維度

**永遠以 2-3 個具體「下一步選項」結尾，讓用戶選**，不要給單一處方。

---

## 常見錯誤

| 錯誤 | 修正 |
|---|---|
| 相信計畫對現狀的敘述 | 每個 load-bearing 宣稱都要 cite file:line 驗證 |
| 用計畫自己的框架評估它 | 先蒸餾終局，再用終局審計畫 |
| 列 nits 而非 gaps | 聚焦「缺什麼」而非錯字 |
| 建議整份推翻 | 骨架通常好，修排序和假設就夠 |
| 跳過架構圖 | 畫不出 loop 就是還沒懂終局 |
| 只讀一個檔案 | Explore 廣度 + Read 深度，平行 |
| 先寫 critique 再讀 code | Code 是 ground truth，推測不是 |
| 沒有 end-state sentence 就開工 | 回 Phase 1，不要偷跑 |

---

## Red Flags — 你正在偏離 reverse thinking

- 逐個 task 評論但還沒先蒸餾終局
- 用計畫本身佐證對 codebase 的宣稱
- 建議「M1 照做就好」而沒檢查假設
- 聚焦「這樣做 work 嗎」而不是「這樣做有沒有推向終局」
- 產出 critique 但沒有一個 file:line cite
- 交付前完全沒列出 gaps

**發現自己在做任何一項 → 回 Phase 1。**

---

## 核心心法

> **計畫的品質不在於它寫得多漂亮，而在於它跟終局的距離。**
>
> 一份完美執行但方向錯的計畫，比一份粗糙但方向對的計畫，更危險。
