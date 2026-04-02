---
description: 深度清潔 — codebase-aware 的文件審計與整理
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(find:*), Bash(wc:*), Bash(rm:*), Bash(mv:*)
argument-hint: "[scope: 'full' | 'docs' | 'memory']"
---

# Deep Housekeep — Codebase-Aware 深度清潔

你是 codebase 的圖書館館長。確保所有文件都跟 code 的真實狀態一致。

**核心原則：文件的價值 = 它與現實的一致性。** 過時的文件比沒有文件更糟。

## Scope Detection

- `full` → 全部清理（預設）
- `docs` → 只清理 `docs/` 目錄
- `memory` → 只清理 memory files + MEMORY.md

## Phase 1: DEEP INVENTORY（parallel subagents）

### Agent A: Docs Audit
```
審計 docs/ 下每份 .md：
1. 讀取內容，提取檔案路徑、class 名稱、API endpoints
2. 用 grep/glob 驗證是否仍存在於 codebase
3. 判斷：✅ CURRENT | 🟡 STALE | 🔴 OBSOLETE | 📋 COMPLETED
4. 特別注意 docs/plans/ 的 checkbox 狀態
```

### Agent B: Memory & State Audit
```
1. 讀取 MEMORY.md + 每個 memory file
2. 交叉比對 memory 中提到的路徑/架構 → codebase
3. 檢查 MEMORY.md 行數（target < 100）
4. 檢查 AGENT_TEST.md / DESIGNER_TEST.md 健康度：
   - last_tested_commit vs HEAD 距離
   - Session History 條數（> 5 需修剪）
```

## Phase 2: CROSS-REFERENCE ANALYSIS

用 extended thinking 交叉分析：

1. **一致性** — memory 決策跟 code 是否矛盾？
2. **冗餘** — 同一件事在多處描述？可從 code/git 推導的不需記錄
3. **缺口** — 重要決策沒被記錄在任何地方？（只報告，不填補）

## Phase 3: ACTION PLAN

**一次性呈現結構化報告，不逐項問。**

```markdown
## Deep Housekeep Report

### 📊 Overall Health
- Docs: N files, X current / Y stale / Z obsolete
- Memory: N files, X lines (target: <100)
- Test logs: AGENT_TEST ✅/⚠️ | DESIGNER_TEST ✅/⚠️

### 🗑️ DELETE (safe to remove)
### ✏️ UPDATE (需要修改內容)
### 📦 ARCHIVE (移到 docs/archive/)
### ✅ KEEP (狀態良好)
### ⚠️ 需要你決定
```

**等使用者確認後執行。**

## Phase 4: EXECUTE

1. DELETE — 刪除確認的檔案
2. UPDATE — 精準修改過時內容
3. ARCHIVE — 移到 `docs/archive/`
4. **MEMORY.md 同步** — 確保 index 與實際 files 一致，行數 < 100

## Phase 5: REPORT

```
Deep Housekeep Complete
═══════════════════════
Deleted:     X files
Updated:     X files
Archived:    X files
MEMORY.md:   Before X lines → After Y lines
```

## Rules

- **先報告，再執行** — 等使用者確認
- **Code 是 source of truth** — 文件跟 code 不一致時，更新文件（不改 code）
- **只管文件** — 不修改 source code
- **MEMORY.md < 100 行** — 硬限制
- **不產生新文件** — 你是清潔工，不是作者
