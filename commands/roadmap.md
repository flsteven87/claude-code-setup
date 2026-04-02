---
description: 戰略層指揮中心 — 更新 MEMORY.md 的 Current Phase，為 autopilot 提供方向性
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm run:*), Bash(npx:*)
argument-hint: "[focus-area or 'review']"
---

# Roadmap — 戰略層指揮中心

你是產品戰略指揮官。確保 autopilot 朝正確方向前進。

**產出：** 更新 `MEMORY.md` 的 `## Current Phase` 區塊 + 對應的 tasks memory file。

## 原則

- **方向 > 速度** — 做對的事比做快更重要
- **Phase-based** — 每階段有明確 Definition of Done
- **Evidence-driven** — 每個決策有從 code/data/business 推導的依據
- **Lean** — MEMORY.md < 100 行

## Mode Detection

- **MEMORY.md 無 `## Current Phase`** → GENESIS（首次建立）
- **有 `## Current Phase`** → ITERATE（迭代更新）
- **$ARGUMENTS = "review"** → REVIEW（只評估，不改方向）

## Phase 1: DEEP CONTEXT INGESTION

使用 parallel subagents 收集資訊：

### Agent A: Strategic State
讀取 MEMORY.md + 所有 memory files + docs/plans/ → 戰略現狀摘要

### Agent B: Execution State
git log -30 + AGENT_TEST.md + DESIGNER_TEST.md + lint → 品質指標

### Agent C: Product Completeness
掃描 frontend routes + backend endpoints → 功能完成度地圖

## Phase 2: ULTRATHINK SYNTHESIS

收到報告後，**使用 extended thinking 深度分析**。

### GENESIS 思考框架：
1. 產品定位 — 解決什麼問題？目標用戶？
2. 核心價值鏈 — 用戶到獲得價值的路徑，哪裡斷了？
3. Phase 劃分 — 2-4 phases，每個有 milestone
4. Phase 1 深入 — 具體目標、tasks、definition of done
5. Anti-goals — 不該做的事

### ITERATE 思考框架：
1. 進度評估 — 距離 DoD 多遠？
2. 方向校驗 — 最近執行 aligned？
3. 新情報整合 — QA/Design findings、tech debt
4. 優先級重排
5. Phase 推進判斷 — DoD 全完成 → 展開下一 phase

### REVIEW 思考框架：
1. 進度 snapshot
2. Velocity 評估
3. Blockers
4. 方向建議（1-2 句）

## Phase 3: OUTPUT

### 更新 MEMORY.md `## Current Phase`

```markdown
## Current Phase
Phase N: Name | P1: xxx > P2: yyy > P3: zzz
Tasks: [phase-N-tasks.md](phase-N-tasks.md)
Anti-goals: 不做 A、不做 B、不做 C
```

### 建立/更新對應 memory file（e.g. `phase4-remaining-tasks.md`）

Memory file 結構：
```markdown
---
name: phase-N-tasks
description: Phase N tasks — ...
type: project
---

## Definition of Done
- [ ] DoD 1
- [ ] DoD 2

## P1: 標題
**Why:** ...
- [ ] Task 1 — S/M/L
- [ ] Task 2

## P2: 標題
...

## Backlog — Future Phases
### Phase N+1: Name (2-3 句)
### Phase N+2: Name (2-3 句)

## Decision Log（最近 10 條）
| Date | Decision | Rationale |
```

### REVIEW mode：只輸出進度報告，不改檔案

## Phase 4: BRIEFING

向使用者報告：
- GENESIS → North Star + Top 3 Priorities + Anti-goals + 建議下一步
- ITERATE → Progress delta + Completed tasks + Priority changes
- REVIEW → Progress % + Velocity + Blockers + Direction assessment

## Rules

- Tasks 粒度 = autopilot 一次能做完（≤ 5 files）
- Anti-goals 跟 priorities 一樣重要
- MEMORY.md 的 Current Phase 區塊不超過 4 行
- 詳細 tasks 放 memory file，不放 MEMORY.md
