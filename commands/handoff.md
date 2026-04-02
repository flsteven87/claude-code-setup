---
description: 更新 MEMORY.md Active Work 區塊，為 /clear 做準備
allowed-tools: Write, Read, Bash(git status:*), Bash(git log:*), Bash(git branch:*), Bash(git diff:*)
---

## 當前 Git 狀態（自動注入）

- **Branch**: !`git branch --show-current`
- **Modified files**: !`git status --porcelain 2>/dev/null`
- **Recent commits**: !`git log --oneline -8 2>/dev/null`

## 你的任務

根據本 session 的完整對話歷史，**更新 MEMORY.md 的 `## Active Work` 區塊**。

不再寫獨立的 handoff 檔案 — MEMORY.md 是唯一的交換點。

---

### 更新內容

```markdown
## Active Work
Last: YYYY-MM-DD — 本 session 做了什麼（1 句摘要）
Decisions: 關鍵決策 → 理由（只記 architectural/design 決策，可省略）
Next:
- 🔴 [高] 最重要的待完成事項
- 🟡 [中] ...
- 🟢 [低] ...
Context: 先讀 X，從 Y 繼續，注意 Z（給下個 session 的提示）
```

### 同時檢查：

1. `## Open Issues` — 本 session 修了什麼？移除已修的。發現新問題？追加。
2. `## Current Phase` — tasks memory file 有完成的？標記 `[x]`。
3. 如果有 memory file 需要更新（新 gotcha、架構決策等），一併更新。

---

寫完後輸出：
> ✅ MEMORY.md 已更新
> 現在可以安全執行 `/clear`，再用 `/catchup` 重建 context。
