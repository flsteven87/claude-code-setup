---
description: 自動執行 autopilot → agent-test → designer-test 閉環循環 N 輪
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(git stash:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(pnpm:*), Bash(npm run:*), Bash(npx:*), Bash(uv run:*), Bash(node:*), Bash(cargo:*), Bash(go :*), Bash(make:*), Bash(gh:*), Bash(curl:*)
argument-hint: "[N=3] number of cycles"
---

# Cycle Mode — 自動閉環循環

執行 N 輪閉環。每輪：autopilot 修 1 個問題 → agent-test 驗證 → designer-test 審查。

**預設 N = 3。**

## 執行流程

```
for each round (1..N):
  1. AUTOPILOT — 從 MEMORY.md 找最高優先工作 → 實作 → verify → commit → push
  2. AGENT-TEST — 驗證修復 + 測試受影響 flow
  3. DESIGNER-TEST — 審查受影響頁面（如果改動涉及 UI）
  4. CHECKPOINT — 記錄成果，決定是否繼續
```

### Step 1: Autopilot Phase
按 `/autopilot` 完整流程執行（Phase 0-6），但**不更新 MEMORY.md Active Work**（最後統一更新）。

### Step 2: Agent-Test Phase
按 `/agent-test` 完整流程執行。自動選 flow（通常是 VERIFY mode）。

### Step 3: Designer-Test Phase
按 `/designer-test` 完整流程執行。**本輪改動不涉及 UI → 跳過。**

### Step 4: Checkpoint

- ✅ 本輪修了什麼？（issue ID + commit hash）
- 🆕 新發現了什麼？
- ⚠️ 是否停止？

## Early Exit

- **連續 2 輪找不到工作** → 佇列已清空
- **連續 2 輪無新發現** → 品質已穩定
- **Context 壓力過大** → 停止寫報告

## Final Report

```
## Cycle Summary — N rounds completed

### 成果
- 修復 X issues: ...
- 新發現 Y issues: ...
- Commits: ...

### 品質趨勢
- Open issues: 開始 M → 結束 N

### 剩餘工作（top 3）

### 建議
- MEMORY.md > 100 行 → `/housekeep memory`
- Phase tasks 全完成 → `/roadmap`
```

然後**更新 MEMORY.md**：
- `## Active Work` — cycle 摘要 + 剩餘 next items
- `## Open Issues` — 修復的移除，新發現的追加
- Current Phase 的 tasks memory file — 標記已完成 tasks

## Rules

- 每輪之間不問使用者確認，全自動
- 每輪 autopilot 只做 1 個小 deliverable
- 某輪修復失敗 → 跳過 agent-test，進下一輪
- Context hygiene — 壓力大就提前結束
