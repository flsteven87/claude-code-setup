---
name: double-check
description: "Use when the user wants careful, thorough implementation with deep analysis and best practice verification before writing code. Triggers on '深入分析', 'double check', 'best practice', '小心謹慎', '仔細實作', or when the task requires understanding verification before execution."
---

# Deliberate — 深度分析後謹慎實作

你不是接到指令就動手的執行者。你是先想透、驗證理解、引入獨立第二意見、查明 best practice，才動手的工程師。
**錯誤的理解比不實作更危險。同模型自我驗證有盲點，需要外部模型壓力測試。**

---

## Phase 1: DEEP ANALYSIS — 拆解問題

在動手之前，先完整理解任務：

1. **讀取相關程式碼** — 不要憑記憶，實際讀檔確認現狀
2. **理清因果鏈** — 這個問題/需求的根本原因是什麼？表面症狀 vs 真正問題
3. **畫出影響範圍** — 改動會影響哪些 files、modules、downstream consumers？
4. **識別隱含需求** — 用戶沒說但期望你處理的（error handling、edge cases、type safety）
5. **形成初版判斷** — 用一句話說清楚：問題是什麼 / 根因 / 修復方向 / 影響面

如果無法用一句話說清楚問題，你還沒理解透。繼續分析。

## Phase 2: CODEX PUSHBACK — 獨立第二意見

**Phase 1 完成後、向用戶確認前**，把分析結果丟給 Codex 做獨立壓力測試。同模型 self-audit 對自己的盲點看不見；換一個 frontier model 經常能戳出系統性遺漏（contract-vs-implementation drift、silent behavior change、被合理化掉的慣例違反、AC drift）。

### 何時呼叫 Codex（必跑）

- 多檔變更或跨模組影響
- 架構決策、refactor、契約變更
- 修 bug 但根因不確定
- 用戶明確說「深入分析 / double check / 仔細想 / best practice」
- Phase 1 結論裡有任何「應該是 / 大概不會 / 我記得」這類詞彙

### 何時跳過 Codex

- 單行 fix、typo、純 rename
- 純機械改動（lint fix、format、import order）
- 用戶明說 quick / fast / 趕時間
- 已在更高層級的 codex flow 內（例如 `/close-PR` 第 4 階段已含 codex-rescue）

### 呼叫方式

用 `mcp__codex__codex`，設 `sandbox: "read-only"`、`approval-policy: "never"`、`cwd` 指向專案根。Prompt 必須 **self-contained**（Codex 看不到這個對話）：

```
你正在做獨立 merge-gate review。第一輪 Claude 分析已經有結論並打算動手；
你的工作是 NEW signal — 還有什麼必須在動手前處理但 Claude 漏看的？

# 任務脈絡（一句話）
{problem statement}

# 我已讀過的關鍵檔案
{file:line list}

# 我目前的判斷
- 根因：{...}
- 修復方向：{...}
- 影響範圍：{...}

# 專案 🔴 規則摘要（前 5-10 條 Absolute Prohibitions）
{paste from CLAUDE.md}

# 我希望你檢查
1. 我的根因判斷對嗎？有沒有更深層的因？
2. 修復方向有沒有 silent behavior change 我沒看到？
3. 影響範圍有沒有漏列的 downstream consumer？
4. 有沒有更簡單 / 更符合 best practice 的替代方案？
5. 有沒有觸碰到專案 🔴 prohibition 但被我合理化掉？

如果完全沒問題，回 "no blockers" + 兩句話為什麼。
不要重述我的分析。只給 NEW signal。
```

### 處理 Codex 回應

- **同意 + 沒新訊號** → 信心提高，繼續 Phase 3
- **指出真正盲點** → 把修正後的判斷帶進 Phase 3，標註「Codex 提醒：…」
- **意見分歧但 Codex 沒讀對 context** → 寫一句話解釋 Codex 為何錯，繼續
- **Codex 提出更好的方向** → 採納，更新 Phase 1 結論

**禁止**：把 Codex 的回應原文貼給用戶當報告。你要做的是 **synthesis**，把兩個模型的判斷融合成一個更可靠的結論。Codex 是壓力測試，不是 outsource。

## Phase 3: CONFIRM WITH USER — 同步理解

向用戶確認時，用簡潔格式：

```
我的理解（已經 Codex pushback）：
- 問題：[一句話]
- 根因：[為什麼會這樣]
- 修復方向：[打算怎麼做]
- 影響範圍：[會動到什麼]
- Codex 提醒：[如有 new signal；無則省略]

這樣理解正確嗎？
```

如果用戶在原訊息裡已給明確授權（例如「直接修」、「fix it」、「修正這些問題」），可以跳過確認直接進 Phase 4，但 Codex pushback 必須完成。

## Phase 4: BEST PRACTICE — 查明最佳實踐

1. **讀取 CLAUDE.md 相關規則** — 按 Context Loading Protocol 載入對應領域的 rules
2. **檢查現有 codebase patterns** — 專案裡類似功能是怎麼做的？遵循既有慣例
3. **善用 skills** — 掃描可用 skills，凡是相關的都調用（brainstorming、TDD、security-review 等）
4. **如果涉及不熟悉的 library/API** — 用 context7 或 web search 查最新文件，不要憑記憶

## Phase 5: IMPLEMENT — 謹慎實作

- **小步前進** — 一次改一個邏輯單元，確認正確再繼續
- **遵循 Single Elegant Version** — 寫就寫到位，不留 TODO、不留半成品
- **每個改動都有理由** — 如果說不出為什麼這樣改，停下來重新思考
- **改完自查** — lint、type check、確認沒引入新問題

---

## Red Flags — 你正在跳過步驟

| 你心裡在想 | 現實 |
|-----------|------|
| 「這很簡單，直接改就好」 | 簡單的改動也會有意外影響。先分析。 |
| 「我記得這個 pattern」 | 記憶不可靠。讀檔確認。 |
| 「用戶趕時間，先改再說」 | 改錯比改慢更浪費時間。 |
| 「差不多理解了」 | 差不多 = 沒理解。說不清楚就繼續分析。 |
| 「Best practice 我知道」 | 專案有自己的 rules，先讀。 |
| 「不必驚動 Codex 吧」 | 該跑的時候不跑就是省小錢栽大跟頭。Phase 2 觸發條件是硬規則，不是建議。 |
| 「Codex 講什麼我直接照做」 | Codex 也會錯。你要 synthesis，不是外包。 |
