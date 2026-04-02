---
description: /clear 後快速重建 session context。從 MEMORY.md 恢復工作狀態
allowed-tools: Read, Glob, Bash(git log:*), Bash(git diff:*), Bash(git branch:*)
argument-hint: "[github-issue-number]"
---

## 當前工作狀態（自動注入）

- **Branch**: !`git branch --show-current`
- **Modified files**: !`git diff HEAD --name-only 2>/dev/null || echo "(no changes)"`
- **Recent commits**: !`git log --oneline -5 2>/dev/null`
- **Diff summary**: !`git diff HEAD --stat 2>/dev/null || echo "(clean)"`

## MEMORY.md Active Work

（使用 Read tool 讀取 MEMORY.md 的 Active Work 區塊）

## 你的任務

1. **讀取 MEMORY.md** — 從 `## Active Work` 了解上次 session 的狀態
2. **讀取 modified files**（如果有 unstaged changes）
3. **如果 Active Work 有 Next items** → 優先處理 🔴 高優先
4. **如果無 Active Work** → 從 git diff 推斷，報告你的理解
5. **如果傳入 issue 號碼（$ARGUMENTS）** → `gh issue view $ARGUMENTS` 載入背景

## 回報格式

繁體中文簡短回報（< 5 行）：
- 目前在哪個任務
- 關鍵檔案狀態
- 建議的下一步

然後直接進入工作。
