---
description: /clear 後快速重建 session context。自動注入 git 狀態與 handoff 文件
allowed-tools: Read, Glob, Bash(git log:*), Bash(git diff:*), Bash(git branch:*)
argument-hint: "[github-issue-number]"
---

## 當前工作狀態（自動注入）

- **Branch**: !`git branch --show-current`
- **Modified files**: !`git diff HEAD --name-only 2>/dev/null || echo "(no changes)"`
- **Recent commits**: !`git log --oneline -5 2>/dev/null`
- **Diff summary**: !`git diff HEAD --stat 2>/dev/null || echo "(clean)"`

## Handoff 文件

!`cat .claude/session-handoff.md 2>/dev/null || echo "(無 handoff 文件，從 git 狀態推斷 context)"`

## 你的任務

1. **讀取所有 modified files** 的當前內容（上方列出的每一個）
2. **如果有 handoff 文件**：繼續其中的「待完成事項」，優先處理標記為高優先的項目
3. **如果沒有 handoff 文件**：根據 git diff 推斷正在進行的工作，報告你的理解
4. **如果傳入 issue 號碼（$ARGUMENTS）**：同時用 `gh issue view $ARGUMENTS` 載入 issue 背景

## 回報格式

用繁體中文簡短回報（< 5 行）：
- 目前在哪個任務
- 關鍵檔案狀態
- 建議的下一步

然後直接進入工作，不要問不必要的問題。
