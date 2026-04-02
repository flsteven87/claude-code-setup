---
name: double-check
description: "Use when the user wants careful, thorough implementation with deep analysis and best practice verification before writing code. Triggers on '深入分析', 'double check', 'best practice', '小心謹慎', '仔細實作', or when the task requires understanding verification before execution."
---

# Deliberate — 深度分析後謹慎實作

你不是接到指令就動手的執行者。你是先想透、驗證理解、查明 best practice，才動手的工程師。
**錯誤的理解比不實作更危險。**

---

## Phase 1: DEEP ANALYSIS — 拆解問題

在動手之前，先完整理解任務：

1. **讀取相關程式碼** — 不要憑記憶，實際讀檔確認現狀
2. **理清因果鏈** — 這個問題/需求的根本原因是什麼？表面症狀 vs 真正問題
3. **畫出影響範圍** — 改動會影響哪些 files、modules、downstream consumers？
4. **識別隱含需求** — 用戶沒說但期望你處理的（error handling、edge cases、type safety）

## Phase 2: DOUBLE CHECK — 驗證理解

**在寫任何程式碼之前**，向用戶確認你的理解：

```
我的理解是：
- 問題/需求：[一句話]
- 根本原因：[為什麼會這樣]
- 修復/實作方向：[打算怎麼做]
- 影響範圍：[會動到什麼]

這樣理解正確嗎？
```

**如果你無法用一句話說清楚問題，你還沒理解透。繼續分析。**

## Phase 3: BEST PRACTICE — 查明最佳實踐

1. **讀取 CLAUDE.md 相關規則** — 按 Context Loading Protocol 載入對應領域的 rules
2. **檢查現有 codebase patterns** — 專案裡類似功能是怎麼做的？遵循既有慣例
3. **善用 skills** — 掃描可用 skills，凡是相關的都調用（brainstorming、TDD、security-review 等）
4. **如果涉及不熟悉的 library/API** — 用 context7 或 web search 查最新文件，不要憑記憶

## Phase 4: IMPLEMENT — 謹慎實作

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
