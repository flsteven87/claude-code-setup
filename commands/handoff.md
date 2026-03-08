---
description: 保存 session 狀態到 .claude/session-handoff.md，為 /clear 做準備。在切換任務或 context 達 70% 前執行
allowed-tools: Write, Read, Bash(git status:*), Bash(git log:*), Bash(git branch:*), Bash(git diff:*)
---

## 當前 Git 狀態（自動注入）

- **Branch**: !`git branch --show-current`
- **Modified files**: !`git status --porcelain 2>/dev/null`
- **Recent commits**: !`git log --oneline -8 2>/dev/null`

## 你的任務

根據本 session 的完整對話歷史，建立 `.claude/session-handoff.md`。

內容必須覆蓋下方所有區段。要求**具體、可操作**，不要模糊。

---

```markdown
# Session Handoff — !`date "+%Y-%m-%d %H:%M"`
Branch: !`git branch --show-current`

## 決策紀錄
<!-- 本 session 做的關鍵決策，特別是 architectural / design 決策。
     格式：決策 → 理由。未來 session 看到這裡就知道「為什麼這樣做」 -->

## 已修改檔案
<!-- 每個檔案一行，說明做了什麼。
     格式：`path/to/file.ts` — 做了什麼（1 句） -->

## 待完成事項
<!-- 按優先序排列，標記依賴關係 -->
- [ ] 🔴 [高] ...
- [ ] 🟡 [中] ...
- [ ] 🟢 [低] ...

## 未解決問題
<!-- Bug、錯誤訊息、或需要注意的技術債。
     格式：問題描述 → 相關檔案/行號（如已知） -->

## 下個 Session 的起點
<!-- 建議先讀哪些檔案、從哪裡繼續、有什麼陷阱要注意 -->
首先讀取：
1. ...
繼續從：...
注意：...
```

---

寫完後輸出：
> ✅ Handoff 已儲存至 `.claude/session-handoff.md`
> 現在可以安全執行 `/clear`，再用 `/catchup` 重建 context。
